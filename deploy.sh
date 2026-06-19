#!/usr/bin/env bash
#
# deploy.sh — Installation et déploiement automatique de WebCrawler SaaS
# Usage : ./deploy.sh            (build + démarrage complet)
#         ./deploy.sh --rebuild  (reconstruction forcée des images)
#
set -euo pipefail

info()  { printf '\033[1;34m[INFO]\033[0m  %s\n' "$*"; }
ok()    { printf '\033[1;32m[ OK ]\033[0m  %s\n' "$*"; }
warn()  { printf '\033[1;33m[WARN]\033[0m  %s\n' "$*"; }
err()   { printf '\033[1;31m[ERR ]\033[0m  %s\n' "$*" >&2; }

# --- 1. Vérification de Docker -----------------------------------------
if ! command -v docker >/dev/null 2>&1; then
    err "Docker n'est pas installé. Installe-le : https://docs.docker.com/engine/install/"
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    err "Docker Compose introuvable (plugin 'docker compose' ou binaire 'docker-compose')."
    exit 1
fi
ok "Docker détecté — utilisation de : $DC"

# --- 2. Fichier .env ----------------------------------------------------
if [ ! -f .env ]; then
    info "Aucun .env trouvé — création depuis .env.example"
    cp .env.example .env

    # Génération d'une SECRET_KEY robuste
    if command -v openssl >/dev/null 2>&1; then
        SECRET=$(openssl rand -base64 64 | tr -dc 'A-Za-z0-9' | head -c 60)
    else
        SECRET=$(head -c 64 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 60)
    fi
    # Remplacement portable (Linux & macOS)
    tmp=$(mktemp)
    sed "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET}|" .env > "$tmp" && mv "$tmp" .env
    ok "SECRET_KEY générée automatiquement."

    warn "IMPORTANT : édite .env avant la mise en production —"
    warn "  -> ALLOWED_HOSTS (ton domaine), DB_PASSWORD, CSRF_TRUSTED_ORIGINS"
    warn "Puis relance : ./deploy.sh"
    read -r -p "Continuer le déploiement avec les valeurs par défaut ? [o/N] " ans
    case "$ans" in
        o|O|oui|y|Y) : ;;
        *) info "Arrêt. Édite .env puis relance ./deploy.sh"; exit 0 ;;
    esac
else
    ok "Fichier .env présent."
fi

# --- 3. Build -----------------------------------------------------------
if [ "${1:-}" = "--rebuild" ]; then
    info "Reconstruction forcée des images (--no-cache)..."
    $DC build --no-cache
else
    info "Construction des images..."
    $DC build
fi

# --- 4. Démarrage -------------------------------------------------------
info "Démarrage des services (db, redis, web, worker, nginx)..."
$DC up -d

# --- 5. État ------------------------------------------------------------
info "État des conteneurs :"
$DC ps

echo
ok "Déploiement terminé."
ok "Application disponible sur : http://localhost  (port 80, via nginx)"
ok "Admin Django : http://localhost/admin"
echo
info "Commandes utiles :"
echo "  $DC logs -f web        # logs du serveur web"
echo "  $DC logs -f worker     # logs du worker Celery"
echo "  $DC exec web python manage.py createsuperuser   # créer un admin"
echo "  $DC down               # arrêter"
