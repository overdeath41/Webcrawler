# Image unique pour les services web, worker et beat.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app/webcrawler_saas

# Toutes les dépendances ont des wheels précompilées : pas de compilateur.
COPY webcrawler_saas/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY docker/ /app/docker/
COPY webcrawler_saas/ ./

# Statiques collectés à la construction (servis par WhiteNoise)
RUN SECRET_KEY=build-only DEBUG=False python manage.py collectstatic --noinput -v 0

RUN chmod +x /app/docker/*.sh \
    && useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/webcrawler_saas/media \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000
