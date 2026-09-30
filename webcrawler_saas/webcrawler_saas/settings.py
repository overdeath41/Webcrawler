"""
Réglages Django — WebCrawler SaaS.

Toute la configuration passe par des variables d'environnement (fichier .env à
la racine du dépôt). En production, DEBUG est faux par défaut et SECRET_KEY est
obligatoire.
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR.parent

# .env à la racine du dépôt (docker compose l'injecte déjà ; utile hors Docker)
load_dotenv(REPO_DIR / ".env")


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_int(name, default):
    return int(os.getenv(name, default))


def env_list(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


TESTING = "test" in sys.argv[1:2]

# ----------------------------------------------------------------------------
# Base
# ----------------------------------------------------------------------------
DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY == "CHANGE_ME":
    if DEBUG or TESTING:
        SECRET_KEY = "dev-only-insecure-key-ne-pas-utiliser-en-production"
    else:
        raise ImproperlyConfigured("SECRET_KEY doit être défini (voir .env.example).")

# Toujours autoriser localhost : le healthcheck Docker passe par là.
ALLOWED_HOSTS = list(dict.fromkeys(env_list("ALLOWED_HOSTS") + ["localhost", "127.0.0.1"]))
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "rest_framework",
    "crawler",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "webcrawler_saas.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "crawler.context_processors.app_limits",
            ],
        },
    },
]

WSGI_APPLICATION = "webcrawler_saas.wsgi.application"

# ----------------------------------------------------------------------------
# Base de données : PostgreSQL si DB_ENGINE le demande, SQLite sinon (dev)
# ----------------------------------------------------------------------------
DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")
if "postgresql" in DB_ENGINE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "webcrawler"),
            "USER": os.getenv("DB_USER", "webcrawler"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / os.getenv("DB_NAME", "db.sqlite3"),
        }
    }

# ----------------------------------------------------------------------------
# Cache (Redis en prod : nécessaire pour un rate limiting partagé entre workers)
# ----------------------------------------------------------------------------
CACHE_URL = os.getenv("CACHE_URL", "")
if CACHE_URL and not TESTING:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": CACHE_URL}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# ----------------------------------------------------------------------------
# Authentification
# ----------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
if TESTING:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

# Anti brute-force sur la connexion
LOGIN_MAX_ATTEMPTS = env_int("LOGIN_MAX_ATTEMPTS", 5)
LOGIN_LOCKOUT_SECONDS = env_int("LOGIN_LOCKOUT_SECONDS", 300)

# ----------------------------------------------------------------------------
# Internationalisation
# ----------------------------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------------
# Fichiers statiques (WhiteNoise) et résultats (jamais servis publiquement)
# ----------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", BASE_DIR / "media"))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if (DEBUG or TESTING)
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------------------------------------------------------
# Sécurité (le site tourne en HTTP sur l'IP du serveur : les options HTTPS
# s'activent via .env le jour où un certificat est en place)
# ----------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = False
HTTPS_ENABLED = env_bool("HTTPS_ENABLED", False)
SESSION_COOKIE_SECURE = HTTPS_ENABLED
CSRF_COOKIE_SECURE = HTTPS_ENABLED
SECURE_SSL_REDIRECT = HTTPS_ENABLED and env_bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = env_int("SECURE_HSTS_SECONDS", 0) if HTTPS_ENABLED else 0
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ----------------------------------------------------------------------------
# Celery
# ----------------------------------------------------------------------------
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_EXPIRES = timedelta(days=1)
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULE = {
    "nettoyage-resultats": {
        "task": "crawler.tasks.cleanup_old_results",
        "schedule": crontab(hour=4, minute=15),
    },
    "taches-bloquees": {
        "task": "crawler.tasks.fail_stale_tasks",
        "schedule": crontab(minute="*/15"),
    },
}

# ----------------------------------------------------------------------------
# API REST
# ----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.UserRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"user": "240/hour"},
}

# ----------------------------------------------------------------------------
# Limites de crawl (cahier des charges MVP)
# ----------------------------------------------------------------------------
MAX_URLS_PER_TASK = env_int("MAX_URLS_PER_TASK", 25)
MAX_ACTIVE_TASKS_PER_USER = env_int("MAX_ACTIVE_TASKS_PER_USER", 5)
CRAWL_DELAY = float(os.getenv("CRAWL_DELAY", 2))
CRAWL_TIMEOUT_SECONDS = env_int("CRAWL_TIMEOUT_SECONDS", 900)
RESULT_RETENTION_DAYS = env_int("RESULT_RETENTION_DAYS", 30)
ALLOWED_TARGET_PORTS = {int(p) for p in env_list("ALLOWED_TARGET_PORTS", "80,443,8080,8443")}
CRAWLER_USER_AGENT = os.getenv(
    "CRAWLER_USER_AGENT", "WebCrawler-SaaS/1.1 (+crawler respectueux de robots.txt)"
)
SCRAPY_PROJECT_DIR = BASE_DIR / "corecrawler"
LEGAL_DOCS_DIR = BASE_DIR / "legal"

# ----------------------------------------------------------------------------
# Journaux (sortie standard : récupérés par `docker compose logs`)
# ----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"django.request": {"level": "WARNING"}},
}
