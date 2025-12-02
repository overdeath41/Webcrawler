# 🚀 Guide d'Installation Complet - WebCrawler SaaS

## 📋 Checklist des Fichiers à Créer

Avant de démarrer, assure-toi que **TOUS** ces fichiers existent :

### ✅ Fichiers de Configuration Scrapy

```bash
# Vérifie que ces fichiers existent dans corecrawler/corecrawler/
ls -la corecrawler/corecrawler/__init__.py
ls -la corecrawler/corecrawler/settings.py
ls -la corecrawler/corecrawler/items.py
ls -la corecrawler/corecrawler/pipelines.py
ls -la corecrawler/corecrawler/middlewares.py
ls -la corecrawler/corecrawler/spiders/__init__.py
```

### ✅ Templates HTML

```bash
# Vérifie que ces fichiers existent dans crawler/templates/crawler/
ls -la crawler/templates/crawler/base.html
ls -la crawler/templates/crawler/login.html
ls -la crawler/templates/crawler/dashboard.html
ls -la crawler/templates/crawler/task_detail.html
```

### ✅ Configuration Docker

```bash
# Vérifie à la racine de webcrawler_saas/
ls -la docker-compose.yml
ls -la Dockerfile
ls -la .gitignore
```

---

## 🛠️ Installation Pas à Pas

### Étape 1 : Créer tous les fichiers manquants

#### 1.1 Fichiers `__init__.py` vides

```bash
cd webcrawler_saas

# Créer les fichiers __init__.py
touch corecrawler/corecrawler/__init__.py
touch corecrawler/corecrawler/spiders/__init__.py
```

#### 1.2 Copier tous les contenus

Pour chaque fichier que je t'ai donné, copie le contenu :

1. **corecrawler/corecrawler/settings.py** → Copie le contenu que j'ai fourni
2. **corecrawler/corecrawler/items.py** → Copie le contenu
3. **corecrawler/corecrawler/pipelines.py** → Copie le contenu
4. **corecrawler/corecrawler/middlewares.py** → Copie le contenu
5. **crawler/templates/crawler/base.html** → Copie le contenu
6. **crawler/templates/crawler/login.html** → Copie le contenu
7. **crawler/templates/crawler/dashboard.html** → Copie le contenu
8. **crawler/templates/crawler/task_detail.html** → Copie le contenu
9. **.gitignore** → Copie le contenu
10. **docker-compose.yml** → Copie le contenu
11. **Dockerfile** → Copie le contenu

---

### Étape 2 : Vérifier l'environnement

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Vérifier Python
python --version  # Doit être 3.10+

# 3. Installer/Mettre à jour les dépendances
pip install -r requirements.txt
```

---

### Étape 3 : Configurer la base de données

```bash
# 1. Appliquer les migrations
python manage.py migrate

# 2. Créer un superutilisateur
python manage.py createsuperuser
# Exemple: username: admin, email: admin@test.com, password: admin123

# 3. Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

---

### Étape 4 : Démarrer les services

#### Option A : Sans Docker (Développement)

**Terminal 1 - Redis :**
```bash
redis-server
# OU avec Docker uniquement pour Redis:
docker run -d -p 6379:6379 redis:alpine
```

**Terminal 2 - Django :**
```bash
cd webcrawler_saas
source venv/bin/activate
python manage.py runserver
```

**Terminal 3 - Celery :**
```bash
cd webcrawler_saas
source venv/bin/activate
celery -A webcrawler_saas worker -l info
```

#### Option B : Avec Docker (Production-like)

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Migrer la base de données
docker-compose exec web python manage.py migrate

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Arrêter tous les services
docker-compose down
```

---

### Étape 5 : Tester l'Application

#### 5.1 Vérifier que tout fonctionne

```bash
# 1. Django check
python manage.py check
# Doit afficher: System check identified no issues

# 2. Vérifier Redis
redis-cli ping
# Doit répondre: PONG

# 3. Vérifier Celery
celery -A webcrawler_saas inspect ping
# Doit afficher: pong

# 4. Vérifier Scrapy
cd corecrawler
scrapy list
# Doit afficher: basic_spider
cd ..
```

#### 5.2 Accéder à l'application

Ouvre ton navigateur :

- **Page d'accueil** : http://localhost:8000
- **Admin Django** : http://localhost:8000/admin
- **Dashboard** : http://localhost:8000/dashboard (après connexion)

#### 5.3 Tester un crawl

1. Va sur http://localhost:8000/register
2. Crée un compte
3. Va sur http://localhost:8000/dashboard
4. Entre des URLs de test :
   ```
   https://example.com
   https://httpbin.org/html
   https://www.google.com
   ```
5. Clique sur "Lancer le crawl"
6. Attends que le statut passe à "Terminé" (auto-refresh)
7. Télécharge le CSV

---

## 🔧 Résolution des Problèmes Courants

### Problème 1 : "ModuleNotFoundError: No module named 'corecrawler'"

**Cause** : Les fichiers `__init__.py` manquent

**Solution** :
```bash
touch corecrawler/corecrawler/__init__.py
touch corecrawler/corecrawler/spiders/__init__.py
```

### Problème 2 : "TemplateDoesNotExist at /"

**Cause** : Les templates ne sont pas dans le bon dossier

**Solution** :
```bash
# Vérifie la structure
ls -la crawler/templates/crawler/
# Doit contenir : base.html, home.html, login.html, etc.
```

### Problème 3 : "Connection refused" pour Redis

**Cause** : Redis n'est pas démarré

**Solution** :
```bash
# Option 1: Redis local
redis-server

# Option 2: Redis Docker
docker run -d -p 6379:6379 redis:alpine

# Vérifier
redis-cli ping
```

### Problème 4 : Celery ne trouve pas les tâches

**Cause** : `__init__.py` manquant dans `webcrawler_saas/`

**Solution** :
```bash
# Vérifie que ce fichier existe et contient:
cat webcrawler_saas/__init__.py

# Doit contenir:
# from .celery import app as celery_app
# __all__ = ('celery_app',)
```

### Problème 5 : "CSRF verification failed"

**Cause** : CORS ou HTTPS mal configuré

**Solution** :
```python
# Dans settings.py, vérifie:
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
```

---

## 📊 Structure des Dossiers Finale

Après avoir créé tous les fichiers, tu devrais avoir :

```
webcrawler_saas/
├── .env                          ✅ Existe déjà
├── .gitignore                    🆕 À CRÉER
├── db.sqlite3                    ✅ Existe déjà
├── manage.py                     ✅ Existe déjà
├── requirements.txt              ✅ Existe déjà
├── docker-compose.yml            🆕 À CRÉER
├── Dockerfile                    🆕 À CRÉER
│
├── corecrawler/
│   ├── scrapy.cfg                ✅ Existe déjà
│   └── corecrawler/
│       ├── __init__.py           🆕 À CRÉER (vide)
│       ├── settings.py           🆕 À CRÉER
│       ├── items.py              🆕 À CRÉER
│       ├── pipelines.py          🆕 À CRÉER
│       ├── middlewares.py        🆕 À CRÉER
│       └── spiders/
│           ├── __init__.py       🆕 À CRÉER (vide)
│           └── basic_spider.py   ✅ Existe (à remplacer)
│
├── crawler/
│   ├── templates/
│   │   └── crawler/
│   │       ├── base.html         🆕 À CRÉER
│   │       ├── home.html         ✅ Existe (à remplacer)
│   │       ├── login.html        🆕 À CRÉER
│   │       ├── register.html     ✅ Existe (à remplacer)
│   │       ├── dashboard.html    🆕 À CRÉER
│   │       └── task_detail.html  🆕 À CRÉER
│   └── [autres fichiers existants]
│
└── webcrawler_saas/
    └── [fichiers de configuration Django existants]
```

---

## ✅ Checklist Finale

Avant de considérer l'installation complète, vérifie :

- [ ] Tous les fichiers `__init__.py` sont créés
- [ ] Tous les fichiers Scrapy sont créés (settings, items, pipelines, middlewares)
- [ ] Tous les templates HTML sont créés (base, login, dashboard, task_detail)
- [ ] `.gitignore` est créé
- [ ] `docker-compose.yml` et `Dockerfile` sont créés
- [ ] Redis démarre sans erreur
- [ ] Django démarre sans erreur
- [ ] Celery démarre sans erreur
- [ ] `scrapy list` affiche "basic_spider"
- [ ] Tu peux créer un compte et te connecter
- [ ] Tu peux lancer un crawl de test
- [ ] Le CSV se télécharge correctement

---

## 🚀 Prochaines Étapes

Une fois l'installation terminée :

1. **Lire la documentation légale** (CGU, Confidentialité)
2. **Tester avec différents sites web**
3. **Personnaliser les templates** selon tes besoins
4. **Ajouter les sélecteurs CSS personnalisés** (Phase 4)
5. **Déployer sur un VPS** (Phase 5)

---

## 📞 Besoin d'Aide ?

Si tu rencontres des problèmes :

1. Vérifie les logs Django : `python manage.py runserver --verbosity 3`
2. Vérifie les logs Celery : `celery -A webcrawler_saas worker -l debug`
3. Vérifie les logs Scrapy dans `/tmp/`
4. Réinitialise complètement :
   ```bash
   rm db.sqlite3
   rm -rf media/*
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

**Bon courage ! 🎉**