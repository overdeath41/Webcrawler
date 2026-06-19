#!/bin/sh
set -e

python docker/wait_for.py "${DB_HOST:-db}" "${DB_PORT:-5432}"

echo "[web] Application des migrations..."
python manage.py migrate --noinput

echo "[web] Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Création optionnelle du superutilisateur (si renseigné dans .env)
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
    echo "[web] Création du superutilisateur ${DJANGO_SUPERUSER_USERNAME} (si absent)..."
    python manage.py createsuperuser --noinput 2>/dev/null || echo "[web] superutilisateur déjà existant, on continue."
fi

echo "[web] Démarrage de Gunicorn..."
exec gunicorn webcrawler_saas.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
