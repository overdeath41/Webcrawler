FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dépendances système (compilation lxml/Twisted/psycopg le cas échéant)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Scripts d'entrée exécutables + utilisateur non-root
RUN chmod +x docker/entrypoint.web.sh docker/entrypoint.worker.sh \
    && useradd --create-home appuser \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
