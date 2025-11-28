from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.conf import settings

class CrawlTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('done', 'Terminé'),
        ('error', 'Erreur'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crawl_tasks')
    urls = models.TextField(help_text="URLs séparées par des virgules ou nouvelles lignes")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    result_file = models.FileField(upload_to='results/%Y/%m/%d/', null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistiques
    urls_count = models.IntegerField(default=0)
    items_scraped = models.IntegerField(default=0)
    
    # ID de tâche Celery
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Tâche de crawl"
        verbose_name_plural = "Tâches de crawl"

    def __str__(self):
        return f"Task #{self.id} - {self.user.username} ({self.status})"
    
    def get_urls_list(self):
        """Retourne la liste des URLs nettoyées"""
        urls = self.urls.replace(',', '\n').split('\n')
        return [url.strip() for url in urls if url.strip()]
    
    def validate_urls_count(self):
        """Vérifie que le nombre d'URLs ne dépasse pas la limite"""
        urls_list = self.get_urls_list()
        if len(urls_list) > settings.MAX_URLS_PER_TASK:
            raise ValueError(f"Maximum {settings.MAX_URLS_PER_TASK} URLs autorisées par tâche")
        return True
    
    def save(self, *args, **kwargs):
        # Calculer le nombre d'URLs
        self.urls_count = len(self.get_urls_list())
        super().save(*args, **kwargs)