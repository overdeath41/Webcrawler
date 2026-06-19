# 🚀 Quick Start Guide - WebCrawler SaaS

## ⚡ Démarrage en 5 minutes

### Prérequis

- Python 3.10+
- Redis (ou Docker)
- Git

### Installation rapide

```bash
# 1. Cloner et entrer dans le projet
git clone <votre-repo>
cd webcrawler_saas

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env si nécessaire

# 5. Initialiser la base de données
python manage.py migrate
python manage.py createsuperuser

# 6. Démarrer Redis (dans un nouveau terminal)
redis-server
# OU avec Docker: docker run -d -p 6379:6379 redis:alpine

# 7. Démarrer Django (terminal 1)
python manage.py runserver

# 8. Démarrer Celery (terminal 2)
celery -A webcrawler_saas worker -l info
```

### ✅ Vérification

Ouvrez votre navigateur et allez sur :
- http://localhost:8000 - Page d'accueil
- http://localhost:8000/admin - Interface admin

---

## 📚 Structure des fichiers à créer

Si vous partez de zéro, créez ces fichiers dans cet ordre :

### 1. Dossiers de base
```bash
mkdir -p templates/crawler
mkdir -p corecrawler/spiders
mkdir -p media/results
mkdir -p logs
```

### 2. Fichiers de configuration

#### .env
```env
SECRET_KEY=django-insecure-CHANGEZ-MOI-EN-PRODUCTION
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

MAX_URLS_PER_TASK=25
CRAWL_DELAY=2
```

#### .gitignore
```gitignore
__pycache__/
*.py[cod]
venv/
db.sqlite3
/media/
/staticfiles/
.env
*.log
.scrapy/
```

### 3. Fichiers __init__.py

Créez des fichiers vides :
```bash
touch corecrawler/__init__.py
touch corecrawler/spiders/__init__.py
```

### 4. Templates HTML

Placez tous les templates dans `templates/crawler/` :
- base.html
- home.html
- login.html
- register.html
- dashboard.html
- task_detail.html

---

## 🧪 Tester l'installation

### Test 1 : Django fonctionne

```bash
python manage.py check
# ✅ Devrait afficher : System check identified no issues
```

### Test 2 : Base de données

```bash
python manage.py showmigrations
# ✅ Devrait montrer les migrations appliquées
```

### Test 3 : Redis

```bash
redis-cli ping
# ✅ Devrait répondre : PONG
```

### Test 4 : Celery

```bash
celery -A webcrawler_saas inspect ping
# ✅ Devrait montrer : pong: OK
```

### Test 5 : Scrapy

```bash
cd corecrawler
scrapy list
# ✅ Devrait afficher : basic_spider
```

### Test 6 : Tests unitaires

```bash
python manage.py test
# ✅ Tous les tests doivent passer
```

---

## 🎯 Utilisation basique

### Via l'interface web

1. **Inscription** : http://localhost:8000/register/
2. **Connexion** : http://localhost:8000/login/
3. **Dashboard** : http://localhost:8000/dashboard/
4. **Créer une tâche** :
   - Entrez vos URLs (une par ligne)
   - Cliquez sur "Lancer le crawl"
5. **Voir les résultats** :
   - Attendez que le statut soit "Terminé"
   - Téléchargez le CSV

### Via l'API

```python
import requests

# 1. Créer une session
session = requests.Session()

# 2. Se connecter
session.post('http://localhost:8000/login/', data={
    'username': 'votre_username',
    'password': 'votre_password'
})

# 3. Créer une tâche
response = session.post('http://localhost:8000/api/tasks/', json={
    'urls': 'https://example.com\nhttps://example2.com'
})
task = response.json()
print(f"Tâche créée : {task['id']}")

# 4. Vérifier le statut
import time
while True:
    response = session.get(f"http://localhost:8000/api/task/{task['id']}/")
    status = response.json()['status']
    print(f"Statut : {status}")
    if status in ['done', 'error']:
        break
    time.sleep(5)
```

---

## 🐛 Problèmes courants

### Problème : "Connection refused" pour Redis

**Solution** :
```bash
# Vérifier que Redis tourne
redis-cli ping

# Si non, démarrer Redis
redis-server

# OU avec Docker
docker run -d -p 6379:6379 redis:alpine
```

### Problème : ImportError pour les modules

**Solution** :
```bash
# Vérifier l'environnement virtuel
which python  # Doit pointer vers venv/bin/python

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : Migrations en erreur

**Solution** :
```bash
# Supprimer la base de données et recommencer
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Problème : Celery ne trouve pas les tâches

**Solution** :
```bash
# Vérifier que __init__.py existe dans webcrawler_saas/
ls webcrawler_saas/__init__.py

# Redémarrer Celery
# Ctrl+C puis relancer
celery -A webcrawler_saas worker -l info
```

### Problème : Templates non trouvés

**Solution** :
```bash
# Vérifier le chemin des templates
ls templates/crawler/

# Vérifier settings.py
python manage.py shell
>>> from django.conf import settings
>>> print(settings.TEMPLATES[0]['DIRS'])
```

---

## 📖 Prochaines étapes

Une fois l'installation réussie :

1. **Personnaliser** : Modifiez les templates à votre goût
2. **Tester** : Lancez des crawls sur des sites de test
3. **Optimiser** : Ajustez CRAWL_DELAY et MAX_URLS_PER_TASK
4. **Sécuriser** : Changez SECRET_KEY avant de déployer
5. **Déployer** : Suivez le DEPLOYMENT_GUIDE.md

---

## 🆘 Besoin d'aide ?

### Logs utiles

```bash
# Logs Django
python manage.py runserver --verbosity 3

# Logs Celery
celery -A webcrawler_saas worker -l debug

# Logs Scrapy (dans les tâches)
# Vérifier /tmp/crawl_result_*.csv
```

### Commandes de debug

```bash
# Shell Django
python manage.py shell
>>> from crawler.models import CrawlTask
>>> CrawlTask.objects.all()

# Shell Celery
celery -A webcrawler_saas shell

# Inspecter Celery
celery -A webcrawler_saas inspect active
celery -A webcrawler_saas inspect registered
```

### Réinitialiser complètement

```bash
# ATTENTION : Supprime toutes les données !
rm db.sqlite3
rm -rf media/results/*
python manage.py migrate
python manage.py createsuperuser
```

---

## ✨ Fonctionnalités principales

| Fonctionnalité | Status | Description |
|---------------|--------|-------------|
| Authentification | ✅ | Inscription, connexion, sessions |
| Dashboard | ✅ | Vue d'ensemble des tâches |
| Crawl asynchrone | ✅ | Via Celery et Scrapy |
| Multi-URLs | ✅ | Jusqu'à 25 URLs par tâche |
| Export CSV | ✅ | Téléchargement des résultats |
| API REST | ✅ | Endpoints CRUD complets |
| Extraction données | ✅ | Titres, descriptions, prix, liens |
| Gestion erreurs | ✅ | Retry et logs détaillés |

---

## 🎓 Ressources

- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Scrapy](https://docs.scrapy.org/)
- [Documentation Celery](https://docs.celeryq.dev/)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

**Prêt à crawler le web !** 🕷️✨

Pour plus de détails, consultez le **README.md** complet.