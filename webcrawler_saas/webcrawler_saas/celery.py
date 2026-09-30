import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webcrawler_saas.settings")

app = Celery("webcrawler_saas")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
