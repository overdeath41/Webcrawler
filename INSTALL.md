# 🚀 Installation & Déploiement — WebCrawler SaaS

Ce paquet contient la migration corrigée et toute la stack Docker pour déployer
le projet sur un serveur en une seule commande.

---

## 1. Où placer chaque fichier

Tous les chemins sont relatifs à `webcrawler_saas/` (le dossier qui contient `manage.py`).

| Fichier livré              | Destination dans le projet                              | Remarque                          |
|----------------------------|---------------------------------------------------------|-----------------------------------|
| `0001_initial.py`          | `crawler/migrations/0001_initial.py`                    | **Remplace** l'ancienne migration |
| `settings.py`              | `webcrawler_saas/settings.py`                           | **Remplace** l'ancien             |
| `requirements.txt`         | `requirements.txt`                                      | **Remplace** l'ancien             |
| `Dockerfile`               | `Dockerfile`                                            | nouveau                           |
| `docker-compose.yml`       | `docker-compose.yml`                                    | nouveau                           |
| `.env.example`             | `.env.example`                                          | nouveau                           |
| `.dockerignore`            | `.dockerignore`                                         | nouveau                           |
| `deploy.sh`                | `deploy.sh`                                             | nouveau (exécutable)              |
| `Makefile`                 | `Makefile`                                              | nouveau (optionnel)               |
| `docker/wait_for.py`       | `docker/wait_for.py`                                    | nouveau                           |
| `docker/entrypoint.web.sh` | `docker/entrypoint.web.sh`                              | nouveau                           |
| `docker/entrypoint.worker.sh` | `docker/entrypoint.worker.sh`                        | nouveau                           |
| `docker/nginx.conf`        | `docker/nginx.conf`                                     | nouveau                           |

---

## 2. La migration

L'ancienne `0001_initial.py` décrivait un modèle obsolète (un seul champ `url`),
incompatible avec `models.py`. La nouvelle a été **générée par Django** à partir
du modèle réel et vérifiée (`makemigrations --check` → aucun changement en
attente).

⚠️ Si tu as une base de dev SQLite existante construite sur l'ancienne migration,
supprime-la avant de migrer :

```bash
rm -f db.sqlite3
python manage.py migrate
```

En Docker (PostgreSQL), la base est neuve : les migrations s'appliquent
automatiquement au premier démarrage, rien à faire.

---

## 3. Déploiement automatique (Docker)

Sur le serveur, depuis le dossier `webcrawler_saas/` :

```bash
chmod +x deploy.sh
./deploy.sh
```

Le script :
1. vérifie que Docker et Docker Compose sont présents ;
2. crée `.env` depuis `.env.example` et génère une `SECRET_KEY` aléatoire ;
3. construit les images ;
4. démarre **db (PostgreSQL), redis, web (Gunicorn), worker (Celery), nginx** ;
5. applique les migrations et le `collectstatic` automatiquement.

➡️ Application accessible sur **http://localhost** (port 80, via nginx).

### Avec le Makefile (optionnel)

```bash
make deploy      # = ./deploy.sh
make logs        # suivre les logs
make superuser   # créer un compte admin
make down        # tout arrêter
```

---

## 4. À configurer avant la vraie production

Édite `.env` puis relance `./deploy.sh` :

- `ALLOWED_HOSTS` → ton nom de domaine
- `DB_PASSWORD` → un mot de passe fort
- `CSRF_TRUSTED_ORIGINS` → `https://ton-domaine.fr`
- `DJANGO_SUPERUSER_*` → si tu veux créer l'admin automatiquement
- Une fois le certificat HTTPS posé (ex. Certbot/Traefik devant nginx) :
  `SECURE_SSL_REDIRECT=True` et `SECURE_HSTS_SECONDS=31536000`

`DEBUG=False` est déjà la valeur par défaut du `.env.example` : les protections
de sécurité (cookies sécurisés, anti-clickjacking, etc.) s'activent
automatiquement.

---

## 5. Architecture déployée

```
            :80
   ┌─────────────────┐
   │   nginx          │  sert /static, /media + reverse proxy
   └────────┬─────────┘
            │ :8000
   ┌────────▼─────────┐      ┌──────────────┐
   │  web (Gunicorn)  │◄────►│ db (Postgres)│
   └────────┬─────────┘      └──────▲───────┘
            │ enqueue               │
   ┌────────▼─────────┐      ┌──────┴───────┐
   │ redis (broker)   │◄────►│ worker       │  exécute Scrapy
   └──────────────────┘      │ (Celery)     │
                             └──────────────┘
```

---

## 6. Points restants (hors périmètre de cette livraison)

Pour mémoire, je n'ai pas encore traité ici — à faire dans un prochain lot :

- le **filtre anti-SSRF** sur les URLs soumises (priorité sécurité) ;
- la **correction du template** `task_detail.html` (syntaxe `in (...)` invalide) ;
- la **validation du nombre d'URLs avant création** dans la vue web ;
- le **rate limiting** sur le login ;
- des **tests** (`tests.py` est vide).

La config HTTPS (certificat) se fait au niveau serveur/nginx selon ton
hébergeur ; je peux te fournir un service Certbot dans le compose si besoin.
