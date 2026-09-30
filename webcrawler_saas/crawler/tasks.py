"""
Tâches Celery : exécution des crawls Scrapy et maintenance.

Scrapy tourne dans un sous-processus (le réacteur Twisted ne redémarre pas
dans un worker Celery de longue durée). Le spider écrit une ligne de
progression par URL traitée ; on la lit en direct pour alimenter la jauge
de l'interface.
"""
import collections
import csv
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from .models import CrawlTask

logger = logging.getLogger(__name__)

PROGRESS_MARKER = "[wc-progress]"
CSV_FIELDS = [
    "url", "status_code", "title", "h1", "description", "prices",
    "links_count", "content_length", "crawled_at", "error",
]


def _feeds_setting(output_path: Path) -> str:
    # CSV en ';' + BOM UTF-8 : s'ouvre directement dans Excel en français.
    return json.dumps({
        str(output_path): {
            "format": "csv",
            "encoding": "utf-8-sig",
            "fields": CSV_FIELDS,
            "overwrite": True,
            "item_export_kwargs": {"delimiter": ";"},
        }
    })


def _scrapy_env() -> dict:
    env = os.environ.copy()
    # netguard.py (anti-SSRF) est partagé avec Django
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(settings.BASE_DIR), env.get("PYTHONPATH")]))
    env["SCRAPY_SETTINGS_MODULE"] = "corecrawler.settings"
    return env


def _count_rows(path: Path) -> int:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return max(0, sum(1 for _ in csv.reader(fh, delimiter=";")) - 1)


@shared_task(bind=True, soft_time_limit=settings.CRAWL_TIMEOUT_SECONDS,
             time_limit=settings.CRAWL_TIMEOUT_SECONDS + 60)
def run_crawl_task(self, task_id):
    try:
        task = CrawlTask.objects.get(pk=task_id)
    except CrawlTask.DoesNotExist:
        logger.error("Tâche %s introuvable", task_id)
        return {"error": "introuvable"}

    # Idempotence : un message rejoué (acks_late) ne relance pas une tâche finie.
    if task.status != CrawlTask.Status.PENDING:
        logger.info("Tâche %s ignorée (statut %s)", task_id, task.status)
        return {"skipped": task.status}

    CrawlTask.objects.filter(pk=task.pk).update(
        status=CrawlTask.Status.RUNNING, started_at=timezone.now(),
        celery_task_id=self.request.id or "", urls_done=0, urls_failed=0,
    )
    logger.info("Démarrage du crawl #%s (%s URLs)", task_id, task.urls_count)

    proc = None
    log_tail = collections.deque(maxlen=40)
    try:
        with tempfile.TemporaryDirectory(prefix=f"crawl_{task_id}_") as tmp:
            tmp = Path(tmp)
            urls_file = tmp / "urls.json"
            output = tmp / "results.csv"
            urls_file.write_text(json.dumps(task.get_urls_list()), encoding="utf-8")

            cmd = [
                sys.executable, "-m", "scrapy", "crawl", "basic_spider",
                "-a", f"urls_file={urls_file}",
                "-s", f"FEEDS={_feeds_setting(output)}",
                "-s", f"DOWNLOAD_DELAY={settings.CRAWL_DELAY}",
                "-s", f"USER_AGENT={settings.CRAWLER_USER_AGENT}",
                "-s", f"WC_ALLOWED_PORTS={','.join(str(p) for p in sorted(settings.ALLOWED_TARGET_PORTS))}",
                "-s", "LOG_LEVEL=INFO",
            ]
            proc = subprocess.Popen(
                cmd, cwd=settings.SCRAPY_PROJECT_DIR, env=_scrapy_env(),
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
            )

            last_flush = 0.0
            done = failed = 0
            for line in proc.stderr:
                if PROGRESS_MARKER in line:
                    done += 1
                    failed += " fail " in line
                    # Mise à jour au plus 2 fois/seconde (ou à la dernière URL)
                    now = time.monotonic()
                    if now - last_flush > 0.5 or done >= task.urls_count:
                        CrawlTask.objects.filter(pk=task.pk).update(urls_done=done, urls_failed=failed)
                        last_flush = now
                else:
                    log_tail.append(line.rstrip())
            returncode = proc.wait()
            CrawlTask.objects.filter(pk=task.pk).update(urls_done=done, urls_failed=failed)

            if returncode != 0:
                raise RuntimeError(f"Scrapy s'est arrêté avec le code {returncode}")
            if not output.exists():
                raise RuntimeError("Aucun fichier de résultats n'a été produit.")

            task.refresh_from_db()
            with open(output, "rb") as fh:
                task.result_file.save(f"mission_{task.pk}.csv", File(fh), save=False)
            task.items_scraped = _count_rows(output)
            task.status = CrawlTask.Status.DONE
            task.completed_at = timezone.now()
            task.error_message = ""
            task.save()

        logger.info("Crawl #%s terminé : %s lignes, %s échecs", task_id, task.items_scraped, task.urls_failed)
        return {"task_id": task_id, "status": "done", "items": task.items_scraped}

    except SoftTimeLimitExceeded:
        _fail(task_id, f"Durée maximale dépassée ({settings.CRAWL_TIMEOUT_SECONDS // 60} min).")
        return {"error": "timeout"}
    except Exception as exc:  # noqa: BLE001 — on veut tout remonter à l'utilisateur
        logger.exception("Erreur crawl #%s", task_id)
        detail = "\n".join(list(log_tail)[-8:])
        _fail(task_id, f"{exc}\n{detail}".strip())
        return {"error": str(exc)}
    finally:
        if proc and proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)


def _fail(task_id, message):
    CrawlTask.objects.filter(pk=task_id).update(
        status=CrawlTask.Status.ERROR, error_message=message[:4000], completed_at=timezone.now(),
    )


@shared_task
def cleanup_old_results():
    """Supprime les CSV plus vieux que RESULT_RETENTION_DAYS (engagement RGPD : 30 j)."""
    cutoff = timezone.now() - timedelta(days=settings.RESULT_RETENTION_DAYS)
    count = 0
    for task in CrawlTask.objects.filter(created_at__lt=cutoff).exclude(result_file="").exclude(result_file=None):
        task.result_file.delete(save=False)
        CrawlTask.objects.filter(pk=task.pk).update(result_file=None)
        count += 1
    logger.info("Nettoyage : %s fichier(s) supprimé(s)", count)
    return count


@shared_task
def fail_stale_tasks():
    """Marque en erreur les missions bloquées (worker redémarré en plein crawl...)."""
    limit = timezone.now() - timedelta(seconds=settings.CRAWL_TIMEOUT_SECONDS + 600)
    stale = CrawlTask.objects.filter(status=CrawlTask.Status.RUNNING, started_at__lt=limit)
    n = stale.update(
        status=CrawlTask.Status.ERROR, completed_at=timezone.now(),
        error_message="Mission interrompue (redémarrage du serveur ?). Utilisez « Relancer ».",
    )
    old_pending = CrawlTask.objects.filter(
        status=CrawlTask.Status.PENDING, created_at__lt=timezone.now() - timedelta(hours=6)
    ).update(
        status=CrawlTask.Status.ERROR, completed_at=timezone.now(),
        error_message="Mission jamais démarrée (file d'attente indisponible). Utilisez « Relancer ».",
    )
    return n + old_pending
