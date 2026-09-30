#!/bin/sh
set -e

python /app/docker/wait_for.py "${DB_HOST:-db}" "${DB_PORT:-5432}"

echo "[web] Migrations..."
python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    python manage.py createsuperuser --noinput >/dev/null 2>&1 \
        && echo "[web] Superutilisateur ${DJANGO_SUPERUSER_USERNAME} créé." \
        || echo "[web] Superutilisateur déjà présent."
fi

echo "[web] Démarrage de Gunicorn (${GUNICORN_WORKERS:-3} workers)..."
exec gunicorn webcrawler_saas.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --threads 2 \
    --timeout 60 \
    --max-requests 2000 --max-requests-jitter 200 \
    --forwarded-allow-ips "*" \
    --access-logfile - \
    --error-logfile -
