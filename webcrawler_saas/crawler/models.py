import re

from django.conf import settings
from django.db import models
from django.utils import timezone

# Séparateurs : espaces/retours ligne, ou virgule/point-virgule suivis d'une URL
# (une virgule à l'intérieur d'une URL est conservée).
URL_SPLIT_RE = re.compile(r"\s+|[,;](?=\s*https?://)", re.IGNORECASE)


def parse_urls(raw: str) -> list[str]:
    """Découpe le texte saisi (lignes, virgules, espaces) et retire les doublons."""
    cleaned = (u.strip().rstrip(",;") for u in URL_SPLIT_RE.split(raw or ""))
    return list(dict.fromkeys(u for u in cleaned if u))


class CrawlTask(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        RUNNING = "running", "En cours"
        DONE = "done", "Terminé"
        ERROR = "error", "Erreur"

    ACTIVE_STATUSES = (Status.PENDING, Status.RUNNING)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="crawl_tasks")
    name = models.CharField("nom", max_length=80, blank=True)
    urls = models.TextField(help_text="Une URL par ligne")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    result_file = models.FileField(upload_to="results/%Y/%m/", null=True, blank=True)
    error_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    urls_count = models.PositiveIntegerField(default=0)
    urls_done = models.PositiveIntegerField(default=0)
    urls_failed = models.PositiveIntegerField(default=0)
    items_scraped = models.PositiveIntegerField(default=0)

    celery_task_id = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "tâche de crawl"
        verbose_name_plural = "tâches de crawl"
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return f"Tâche #{self.pk} — {self.user} ({self.status})"

    def get_urls_list(self):
        return parse_urls(self.urls)

    @property
    def display_name(self):
        return self.name or f"Mission #{self.pk}"

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES

    @property
    def progress_percent(self):
        if self.status == self.Status.DONE:
            return 100
        if not self.urls_count:
            return 0
        return min(100, round(100 * self.urls_done / self.urls_count))

    @property
    def duration(self):
        """Durée d'exécution (timedelta) ou None."""
        start = self.started_at or self.created_at
        end = self.completed_at or (timezone.now() if self.status == self.Status.RUNNING else None)
        if not start or not end:
            return None
        return end - start

    @property
    def duration_display(self):
        d = self.duration
        if d is None:
            return "—"
        seconds = int(d.total_seconds())
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def save(self, *args, **kwargs):
        self.urls_count = len(self.get_urls_list())
        super().save(*args, **kwargs)
