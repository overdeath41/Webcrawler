from django.conf import settings


def app_limits(request):
    return {
        "MAX_URLS_PER_TASK": settings.MAX_URLS_PER_TASK,
        "CRAWL_DELAY": settings.CRAWL_DELAY,
        "RESULT_RETENTION_DAYS": settings.RESULT_RETENTION_DAYS,
    }
