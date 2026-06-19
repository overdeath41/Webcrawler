import os
import csv
import logging
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from .models import CrawlTask
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import subprocess
import json

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def run_crawl_task(self, task_id):
    """
    Exécute une tâche de crawl avec Scrapy
    """
    try:
        task = CrawlTask.objects.get(id=task_id)
        task.status = 'running'
        task.celery_task_id = self.request.id
        task.save()
        
        logger.info(f"Démarrage du crawl pour la tâche {task_id}")
        
        # Récupérer les URLs
        urls = task.get_urls_list()
        
        if not urls:
            raise ValueError("Aucune URL valide fournie")
        
        # Créer le fichier de sortie temporaire
        output_file = f"/tmp/crawl_result_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Préparer les arguments pour Scrapy
        scrapy_settings = {
            'FEED_FORMAT': 'csv',
            'FEED_URI': output_file,
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': settings.CRAWL_DELAY,
            'CONCURRENT_REQUESTS': 1,
            'USER_AGENT': 'WebCrawler-SaaS/1.0 (+https://votresite.com/bot)',
        }
        
        # Exécuter Scrapy via subprocess (plus stable que CrawlerProcess dans Celery)
        urls_json = json.dumps(urls)
        
        cmd = [
            'scrapy', 'crawl', 'basic_spider',
            '-a', f'urls={urls_json}',
            '-s', f'FEED_FORMAT=csv',
            '-s', f'FEED_URI={output_file}',
            '-s', 'ROBOTSTXT_OBEY=True',
            '-s', f'DOWNLOAD_DELAY={settings.CRAWL_DELAY}',
            '-s', 'CONCURRENT_REQUESTS=1',
        ]
        
        # Changer vers le répertoire corecrawler
        scrapy_dir = os.path.join(settings.BASE_DIR, 'corecrawler')
        
        result = subprocess.run(
            cmd,
            cwd=scrapy_dir,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes max
        )
        
        if result.returncode != 0:
            raise Exception(f"Erreur Scrapy: {result.stderr}")
        
        # Vérifier que le fichier a été créé
        if not os.path.exists(output_file):
            raise Exception("Le fichier de résultats n'a pas été créé")
        
        # Lire et sauvegarder le fichier
        with open(output_file, 'rb') as f:
            file_content = f.read()
            filename = f"crawl_results_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            task.result_file.save(filename, ContentFile(file_content), save=False)
        
        # Compter les items scrapés
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            items_count = sum(1 for row in reader) - 1  # -1 pour l'en-tête
        
        task.items_scraped = max(0, items_count)
        task.status = 'done'
        task.completed_at = datetime.now()
        task.save()
        
        # Nettoyer le fichier temporaire
        os.remove(output_file)
        
        logger.info(f"Crawl terminé pour la tâche {task_id}: {items_count} items")
        
        return {
            'task_id': task_id,
            'status': 'done',
            'items_scraped': items_count
        }
        
    except CrawlTask.DoesNotExist:
        logger.error(f"Tâche {task_id} introuvable")
        return {'error': 'Tâche introuvable'}
    
    except Exception as e:
        logger.error(f"Erreur lors du crawl {task_id}: {str(e)}")
        try:
            task = CrawlTask.objects.get(id=task_id)
            task.status = 'error'
            task.error_message = str(e)
            task.completed_at = datetime.now()
            task.save()
        except:
            pass
        
        return {'error': str(e)}


@shared_task
def cleanup_old_results():
    """
    Tâche périodique pour nettoyer les anciens fichiers de résultats
    À exécuter quotidiennement
    """
    from datetime import timedelta
    from django.utils import timezone
    
    cutoff_date = timezone.now() - timedelta(days=30)
    old_tasks = CrawlTask.objects.filter(created_at__lt=cutoff_date)
    
    count = 0
    for task in old_tasks:
        if task.result_file:
            task.result_file.delete()
            count += 1
    
    logger.info(f"Nettoyage: {count} fichiers supprimés")
    return f"Supprimé {count} fichiers"