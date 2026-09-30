# WebCrawler SaaS

Plateforme no-code d'extraction de données web (Django · Scrapy · Celery),
pensée pour les e-commerçants et marketeurs francophones. L'utilisateur colle
jusqu'à 25 adresses, le robot visite chaque page en respectant `robots.txt`, et
un CSV prêt pour Excel est disponible au téléchargement.

Interface : thème « menu de RPG rétro » (fenêtres bleues biseautées, curseur,
jauges de progression en temps réel).

---

## Architecture sur le serveur

```
 Navigateur ──► http://IP_DU_SERVEUR/  (port 80)
                     │
          ┌──────────▼───────────┐   nginx de l'hôte Ubuntu
          │ /etc/nginx/sites-…/  │   (cohabite avec vos autres sites)
          │   webcrawler.conf    │
          └──────────┬───────────┘
                     │ 127.0.0.1:8000 (jamais exposé au réseau)
   ┌─────────────────┼──────────────── Docker Compose ─────────────────┐
   │  web (Gunicorn + WhiteNoise)   worker (Celery → Scrapy)   beat   │
   │           │                          │                           │
   │     db (PostgreSQL 16)          redis (file + cache)             │
   └───────────────────────────────────────────────────────────────────┘
```

* Aucun port autre que 80 n'est ouvert : PostgreSQL et Redis restent dans le
  réseau Docker, Gunicorn n'écoute que sur `127.0.0.1`.
* Les CSV ne sont jamais servis publiquement : le téléchargement passe par
  Django, qui vérifie que la mission appartient bien à l'utilisateur.

## Installation (Ubuntu 22.04 / 24.04)

```bash
git clone https://github.com/overdeath41/Webcrawler.git
cd Webcrawler
./deploy.sh
```

Le script est idempotent (relançable sans risque) et :

1. installe Docker, Compose v2 et nginx s'ils manquent (après confirmation) ;
2. crée `.env` avec une `SECRET_KEY` et un mot de passe PostgreSQL aléatoires,
   et détecte l'IP du serveur ;
3. construit l'image et démarre `db`, `redis`, `web`, `worker`, `beat` ;
4. installe le site nginx (`server_name` = IP + nom d'hôte), vérifie la
   configuration avec `nginx -t` et ne recharge nginx que si elle est valide
   (sinon l'ancienne configuration est restaurée) ;
5. ouvre le port 80 dans `ufw` si le pare-feu est actif (après confirmation).

Le site est ensuite accessible sur `http://IP_DU_SERVEUR/`.

Créer un compte administrateur : `make superuser` → `http://IP_DU_SERVEUR/admin/`.

### Cohabitation avec un nginx existant

Le site est déclaré avec `server_name <IP> <hostname>` **sans** `default_server` :
il répond aux requêtes adressées à l'IP du serveur sans toucher aux autres
sites. Si un autre site déclare déjà cette IP, le script le signale avant
d'écrire quoi que ce soit. Pour que WebCrawler réponde à *toute* requête
(y compris par un nom inconnu), mettre `NGINX_DEFAULT_SERVER=True` dans `.env`.

## Exploitation

| Commande          | Effet                                                   |
|-------------------|---------------------------------------------------------|
| `make logs`       | journaux en direct de tous les services                 |
| `make ps`         | état des conteneurs                                     |
| `make update`     | `git pull` puis redéploiement                           |
| `make backup`     | sauvegarde PostgreSQL + CSV dans `./backups/`           |
| `make restore DUMP=…` | restauration d'une sauvegarde PostgreSQL            |
| `make test`       | suite de tests dans le conteneur                        |
| `make down`       | arrêt (les données restent dans les volumes Docker)     |

Tâches planifiées (service `beat`) : suppression des CSV de plus de 30 jours
(engagement RGPD) chaque nuit, et passage en erreur des missions bloquées
toutes les 15 minutes.

## Configuration (`.env`)

Voir `.env.example`, entièrement commenté. Réglages utiles pour un Xeon :
`GUNICORN_WORKERS`, `CELERY_CONCURRENCY` (crawls simultanés) et
`WORKER_MEM_LIMIT`. Ne modifiez jamais `DB_PASSWORD` après le premier
démarrage (la base a été initialisée avec).

Passage en HTTPS le jour où un nom de domaine existe : certificat côté nginx
(Certbot), puis `HTTPS_ENABLED=True` et `CSRF_TRUSTED_ORIGINS=https://…`.

## Sécurité intégrée

* **Anti-SSRF** : refus des adresses internes/privées (127.x, 10.x, 192.168.x,
  169.254.x, IPv6 locales, IPv4 encapsulées…), des identifiants dans l'URL et
  des ports non standards, à la saisie **et** dans Scrapy (middleware +
  résolveur DNS vérifiant l'IP réellement contactée, redirections comprises).
* Limitation des tentatives de connexion (5 échecs → blocage 5 min, par IP et
  par identifiant), déconnexion en POST, mots de passe Argon2.
* 5 missions actives maximum par utilisateur, 25 URLs par mission, délai
  minimal entre deux pages, `robots.txt` respecté, User-Agent identifiable.

## Développement local

```bash
cd webcrawler_saas
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt
DEBUG=True python manage.py migrate
DEBUG=True python manage.py runserver
DEBUG=True python manage.py test crawler      # 30 tests, dont 2 crawls réels
```

Sans Redis, lancer un worker n'est pas possible ; pour tester un crawl en local,
utiliser `ALLOW_PRIVATE_TARGETS=True` uniquement sur sa machine de dev.

> ⚠️ Une ancienne base SQLite créée avec l'ancienne migration est incompatible :
> supprimer `webcrawler_saas/db.sqlite3` puis relancer `migrate`.

## Arborescence

```
.
├── deploy.sh, Makefile, Dockerfile, docker-compose.yml, .env.example
├── docker/            scripts d'entrée des conteneurs
├── nginx/             modèle de site nginx pour l'hôte
├── docs/              spécifications MVP
└── webcrawler_saas/   projet Django
    ├── netguard.py    garde-fou anti-SSRF partagé Django/Scrapy
    ├── crawler/       application (vues, tâches Celery, templates, thème)
    ├── corecrawler/   projet Scrapy (spider, middlewares, résolveur, pipelines)
    └── legal/         CGU, confidentialité, utilisation responsable (rendues sur le site)
```
