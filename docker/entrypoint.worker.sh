#!/bin/sh
set -e

python /app/docker/wait_for.py "${DB_HOST:-db}" "${DB_PORT:-5432}"
python /app/docker/wait_for.py "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}"

echo "[worker] Démarrage du worker Celery (concurrence ${CELERY_CONCURRENCY:-2})..."
exec celery -A webcrawler_saas worker \
    -l info \
    --concurrency "${CELERY_CONCURRENCY:-2}" \
    --max-tasks-per-child 50
