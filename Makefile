# Raccourcis de gestion — détecte automatiquement docker compose v2/v1
DC := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

.PHONY: deploy up down restart build rebuild logs ps migrate superuser shell-web shell-worker

deploy:        ## Installation + déploiement complet
	./deploy.sh

up:            ## Démarrer les services
	$(DC) up -d

down:          ## Arrêter les services
	$(DC) down

restart:       ## Redémarrer
	$(DC) restart

build:         ## Construire les images
	$(DC) build

rebuild:       ## Reconstruire sans cache
	$(DC) build --no-cache

logs:          ## Logs de tous les services
	$(DC) logs -f

ps:            ## État des conteneurs
	$(DC) ps

migrate:       ## Appliquer les migrations
	$(DC) exec web python manage.py migrate

superuser:     ## Créer un compte admin
	$(DC) exec web python manage.py createsuperuser

shell-web:     ## Shell dans le conteneur web
	$(DC) exec web sh

shell-worker:  ## Shell dans le conteneur worker
	$(DC) exec worker sh
