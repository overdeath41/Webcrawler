# Raccourcis d'exploitation — WebCrawler SaaS
DC := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "sudo docker compose")

.PHONY: help deploy update rebuild up down restart logs ps superuser shell test backup restore

help:            ## Affiche cette aide
	@grep -E '^[a-z]+:.*##' Makefile | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

deploy:          ## Installation / mise à jour complète
	./deploy.sh

update:          ## git pull + redéploiement
	git pull --ff-only && ./deploy.sh --yes

rebuild:         ## Reconstruction sans cache
	./deploy.sh --rebuild

up:              ## Démarrer la pile
	$(DC) up -d

down:            ## Arrêter la pile (les données sont conservées)
	$(DC) down

restart:         ## Redémarrer web + worker
	$(DC) restart web worker beat

logs:            ## Journaux en direct
	$(DC) logs -f --tail 100

ps:              ## État des conteneurs
	$(DC) ps

superuser:       ## Créer un compte administrateur
	$(DC) exec web python manage.py createsuperuser

shell:           ## Shell Django
	$(DC) exec web python manage.py shell

test:            ## Lancer la suite de tests dans le conteneur
	$(DC) run --rm --no-deps -e DB_ENGINE=sqlite web python manage.py test crawler

backup:          ## Sauvegarde base + résultats dans ./backups/
	@mkdir -p backups
	$(DC) exec -T db sh -c 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -Fc' > backups/db_$$(date +%Y%m%d_%H%M).dump
	$(DC) run --rm --no-deps -T web tar czf - -C /app/webcrawler_saas media > backups/media_$$(date +%Y%m%d_%H%M).tar.gz
	@ls -lh backups | tail -4

restore:         ## Restaure une sauvegarde : make restore DUMP=backups/db_xxx.dump
	@test -n "$(DUMP)" || (echo "Usage : make restore DUMP=backups/db_xxx.dump" && exit 1)
	$(DC) exec -T db sh -c 'pg_restore -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" --clean --if-exists' < $(DUMP)
