#!/bin/sh
set -e

python docker/wait_for.py "${DB_HOST:-db}" "${DB_PORT:-5432}"
python docker/wait_for.py "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}"

echo "[worker] Démarrage du worker Celery..."
exec celery -A webcrawler_saas worker \
    -l info \
    --concurrency "${CELERY_CONCURRENCY:-2}"
