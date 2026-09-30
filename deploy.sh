#!/usr/bin/env bash
#
# deploy.sh — installation / mise à jour de WebCrawler SaaS sur Ubuntu
#
#   ./deploy.sh              installe ou met à jour (idempotent)
#   ./deploy.sh --rebuild    reconstruit les images sans cache
#   ./deploy.sh --yes        répond « oui » à toutes les questions
#
# Architecture : Docker Compose (PostgreSQL, Redis, Gunicorn, Celery) +
# nginx de l'hôte sur le port 80 → site accessible sur http://IP_DU_SERVEUR/
#
set -euo pipefail
cd "$(dirname "$0")"

REBUILD=0; ASSUME_YES=0
for arg in "$@"; do
    case "$arg" in
        --rebuild) REBUILD=1 ;;
        --yes|-y)  ASSUME_YES=1 ;;
        -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
        *) echo "Option inconnue : $arg" >&2; exit 2 ;;
    esac
done

info() { printf '\033[1;34m[INFO]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[ OK ]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[WARN]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[ERR ]\033[0m %s\n' "$*" >&2; exit 1; }
ask()  { # ask "question" → 0 si oui
    [ "$ASSUME_YES" = 1 ] && return 0
    local ans; read -r -p "$1 [o/N] " ans
    case "$ans" in o|O|oui|y|Y|yes) return 0 ;; *) return 1 ;; esac
}
rand() { head -c 256 /dev/urandom | tr -dc 'A-Za-z0-9' | head -c "$1"; }

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    command -v sudo >/dev/null || die "sudo est requis (ou lance le script en root)."
    SUDO="sudo"
fi

# ---------------------------------------------------------------------------
# 1. Système
# ---------------------------------------------------------------------------
if [ -r /etc/os-release ]; then . /etc/os-release; info "Système : ${PRETTY_NAME:-inconnu}"; fi
[ "${ID:-}" = "ubuntu" ] || warn "Script prévu pour Ubuntu ; on continue quand même."

APT_UPDATED=0
apt_install() {
    if [ "$APT_UPDATED" = 0 ]; then $SUDO apt-get update -qq; APT_UPDATED=1; fi
    $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$@"
}

# ---------------------------------------------------------------------------
# 2. Docker + Compose v2
# ---------------------------------------------------------------------------
if ! command -v docker >/dev/null; then
    ask "Docker n'est pas installé. L'installer (paquets Ubuntu docker.io + docker-compose-v2) ?" \
        || die "Docker est requis."
    apt_install docker.io docker-compose-v2
    $SUDO systemctl enable --now docker
fi
DOCKER="docker"
if ! docker info >/dev/null 2>&1; then
    DOCKER="$SUDO docker"
    $DOCKER info >/dev/null 2>&1 || die "Impossible de joindre le démon Docker."
    warn "Docker utilisé via sudo (astuce : sudo usermod -aG docker $USER, puis reconnexion)."
fi
if $DOCKER compose version >/dev/null 2>&1; then
    DC="$DOCKER compose"
elif command -v docker-compose >/dev/null; then
    DC="$SUDO docker-compose"; warn "docker-compose v1 détecté : la v2 est recommandée."
else
    ask "Plugin Docker Compose absent. Installer docker-compose-v2 ?" || die "Compose est requis."
    apt_install docker-compose-v2; DC="$DOCKER compose"
fi
ok "Docker : $($DOCKER --version | cut -d, -f1) — Compose : $($DC version --short 2>/dev/null || echo v1)"

# ---------------------------------------------------------------------------
# 3. nginx de l'hôte
# ---------------------------------------------------------------------------
if ! command -v nginx >/dev/null; then
    ask "nginx n'est pas installé sur l'hôte. L'installer ?" || die "nginx est requis."
    apt_install nginx
    $SUDO systemctl enable --now nginx
fi
ok "nginx : $(nginx -v 2>&1 | cut -d/ -f2)"
command -v curl >/dev/null || apt_install curl

# ---------------------------------------------------------------------------
# 4. Fichier .env
# ---------------------------------------------------------------------------
set_env() { # set_env CLE valeur  (remplace ou ajoute)
    local key="$1" val="$2" tmp; tmp=$(mktemp)
    if grep -q "^${key}=" .env; then
        awk -v k="$key" -v v="$val" 'BEGIN{FS=OFS="="} $1==k{print k"="v; next} {print}' .env > "$tmp"
    else
        cat .env > "$tmp"; echo "${key}=${val}" >> "$tmp"
    fi
    cat "$tmp" > .env; rm -f "$tmp"
}
get_env() { grep -E "^$1=" .env 2>/dev/null | tail -1 | cut -d= -f2- || true; }

if [ ! -f .env ]; then
    cp .env.example .env
    chmod 600 .env
    info "Fichier .env créé depuis .env.example"
fi
case "$(get_env SECRET_KEY)" in ""|CHANGE_ME) set_env SECRET_KEY "$(rand 64)"; ok "SECRET_KEY générée." ;; esac
case "$(get_env DB_PASSWORD)" in
    ""|CHANGE_ME)
        # Attention : ne jamais changer ce mot de passe une fois la base créée
        set_env DB_PASSWORD "$(rand 32)"; ok "Mot de passe PostgreSQL généré." ;;
esac

SERVER_IP="$(get_env SERVER_IP)"
if [ -z "$SERVER_IP" ]; then
    # IP de l'interface de sortie par défaut (ignore docker0, bridges, etc.)
    SERVER_IP="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}')"
    [ -n "$SERVER_IP" ] || SERVER_IP="$(hostname -I | awk '{print $1}')"
    [ -n "$SERVER_IP" ] || die "IP du serveur introuvable : renseigne SERVER_IP dans .env"
    set_env SERVER_IP "$SERVER_IP"
    ok "IP du serveur détectée : $SERVER_IP"
fi
HOST_SHORT="$(hostname -s 2>/dev/null || hostname)"
if [ -z "$(get_env ALLOWED_HOSTS)" ]; then
    set_env ALLOWED_HOSTS "${SERVER_IP},${HOST_SHORT},${HOST_SHORT}.local,localhost,127.0.0.1"
fi
APP_PORT="$(get_env APP_PORT)"; APP_PORT="${APP_PORT:-8000}"

# Port local libre ? (sauf s'il est déjà tenu par notre propre conteneur)
if ss -ltnH "sport = :$APP_PORT" 2>/dev/null | grep -q . \
   && ! $DC ps --status running --services 2>/dev/null | grep -qx web; then
    die "Le port local $APP_PORT est déjà utilisé sur ce serveur. Choisis un autre APP_PORT dans .env."
fi

# ---------------------------------------------------------------------------
# 5. Construction et démarrage de la pile
# ---------------------------------------------------------------------------
if [ "$REBUILD" = 1 ]; then
    info "Reconstruction complète des images..."; $DC build --no-cache --pull
else
    info "Construction des images..."; $DC build --pull
fi
info "Démarrage : db, redis, web, worker, beat"
$DC up -d --remove-orphans

info "Attente du démarrage de l'application..."
for i in $(seq 1 60); do
    if curl -fsS "http://127.0.0.1:${APP_PORT}/healthz/" >/dev/null 2>&1; then ok "Application prête."; break; fi
    [ "$i" = 60 ] && { $DC logs --tail 60 web; die "L'application ne répond pas (logs ci-dessus)."; }
    sleep 2
done

# ---------------------------------------------------------------------------
# 6. Site nginx sur l'hôte
# ---------------------------------------------------------------------------
SITE_AVAIL=/etc/nginx/sites-available/webcrawler.conf
SITE_ENABLED=/etc/nginx/sites-enabled/webcrawler.conf
SERVER_NAMES="$(get_env ALLOWED_HOSTS | tr ',' '\n' | grep -vxE 'localhost|127\.0\.0\.1|\*' | paste -sd' ' -)"
[ -n "$SERVER_NAMES" ] || SERVER_NAMES="$SERVER_IP"
DEFAULT_SERVER=""
case "$(get_env NGINX_DEFAULT_SERVER | tr 'A-Z' 'a-z')" in true|1|yes|oui) DEFAULT_SERVER=" default_server" ;; esac

# Un autre site sert-il déjà cette IP sur le port 80 ?
IP_RE="${SERVER_IP//./\\.}"
if $SUDO nginx -T 2>/dev/null \
     | awk -v f="${SITE_ENABLED}:" '/^# configuration file /{skip=($4==f)} !skip' \
     | grep -Eq "server_name[^;]*[[:space:]]${IP_RE}([[:space:]]|;)"; then
    warn "Un autre site nginx déclare déjà server_name $SERVER_IP : il y aura un conflit."
    ask "Continuer malgré tout ?" || die "Arrêt : ajuste la configuration nginx existante."
fi
if [ -n "$DEFAULT_SERVER" ] && [ -e /etc/nginx/sites-enabled/default ]; then
    if ask "NGINX_DEFAULT_SERVER=True : désactiver le site « default » d'Ubuntu (page Welcome to nginx) ?"; then
        $SUDO rm -f /etc/nginx/sites-enabled/default
    else
        DEFAULT_SERVER=""; warn "default_server ignoré pour éviter un conflit."
    fi
fi

tmp=$(mktemp)
sed -e "s|__SERVER_NAMES__|${SERVER_NAMES}|" \
    -e "s|__APP_PORT__|${APP_PORT}|" \
    -e "s|__DEFAULT_SERVER__|${DEFAULT_SERVER}|" \
    nginx/webcrawler.conf.template > "$tmp"
BACKUP=""
if [ -f "$SITE_AVAIL" ]; then BACKUP=$(mktemp); $SUDO cp "$SITE_AVAIL" "$BACKUP"; fi
$SUDO install -m 644 "$tmp" "$SITE_AVAIL"; rm -f "$tmp"
$SUDO ln -sf "$SITE_AVAIL" "$SITE_ENABLED"

if $SUDO nginx -t 2>/tmp/nginx-test.log; then
    $SUDO systemctl reload nginx
    ok "Site nginx installé : $SITE_AVAIL (server_name ${SERVER_NAMES})"
else
    cat /tmp/nginx-test.log >&2
    if [ -n "$BACKUP" ]; then $SUDO cp "$BACKUP" "$SITE_AVAIL"; else $SUDO rm -f "$SITE_ENABLED" "$SITE_AVAIL"; fi
    die "Configuration nginx invalide : ancienne configuration restaurée, rien n'a été rechargé."
fi

# ---------------------------------------------------------------------------
# 7. Pare-feu
# ---------------------------------------------------------------------------
if command -v ufw >/dev/null && $SUDO ufw status 2>/dev/null | grep -q "Status: active"; then
    if ! $SUDO ufw status | grep -Eq '^(80/tcp|80|Nginx (HTTP|Full))[[:space:]]+ALLOW'; then
        ask "ufw est actif et le port 80 n'est pas ouvert. L'ouvrir ?" && $SUDO ufw allow 80/tcp
    fi
fi

# ---------------------------------------------------------------------------
# 8. Vérification finale à travers nginx
# ---------------------------------------------------------------------------
if curl -fsS -H "Host: ${SERVER_IP}" "http://127.0.0.1/healthz/" >/dev/null 2>&1; then
    ok "nginx → application : OK"
else
    warn "nginx ne relaie pas encore correctement (voir /var/log/nginx/webcrawler.error.log)."
fi

$DC ps
echo
ok "WebCrawler est en ligne : http://${SERVER_IP}/"
ok "Administration       : http://${SERVER_IP}/admin/"
echo
info "Commandes utiles : make logs | make superuser | make backup | make update"
