# 📋 Spécifications Fonctionnelles MVP
## WebCrawler SaaS - Version 1.0

**Auteur** : Thumser Luc  
**Date** : 13 novembre 2025  
**Objectif** : Définir précisément le MVP pour un lancement en 12 semaines

---

## 🎯 Vision Produit

### Problème Identifié
Les e-commerçants, marketeurs et entrepreneurs **non-techniques** ont besoin d'extraire des données web (prix, produits, contenus) mais :
- ❌ Ne savent pas coder
- ❌ Trouvent les outils existants trop complexes (Scrapy, Selenium)
- ❌ N'ont pas le budget pour des solutions entreprise (ParseHub, Import.io à 300€+/mois)
- ❌ Se méfient des scrapers non-européens (RGPD)

### Solution MVP
Une plateforme **no-code en français**, **hébergée en France**, permettant de :
1. ✅ Crawler jusqu'à 25 URLs simultanément
2. ✅ Extraire des données via sélecteurs CSS simples
3. ✅ Télécharger les résultats en CSV
4. ✅ Respecter robots.txt automatiquement
5. ✅ Payer un tarif transparent (40-50€/mois)

---

## 👤 Persona Principal : "Marc, E-Commerçant"

**Profil**
- 👨 Homme, 35 ans
- 💼 Gérant d'une boutique Shopify (20K€/mois CA)
- 🎯 Veut surveiller les prix de 3 concurrents
- 💻 Niveau technique : utilise Excel, pas de code
- 💰 Budget : 50€/mois max
- 🇫🇷 Exigence : solution française (RGPD)

**Besoins**
1. Extraire 10 URLs de produits par concurrent (30 URLs total)
2. Récupérer : titre, prix, disponibilité
3. Automatiser 1x/jour
4. Exporter en CSV pour import Excel

**Frustrations actuelles**
- ParseHub : trop cher (299$/mois) et en anglais
- Scrapy : trop technique, nécessite du code
- VA freelance : 500€/mois, pas fiable

---

## 🚀 Fonctionnalités MVP (MoSCoW)

### ✅ MUST HAVE (Obligatoire pour le MVP)

#### 1. Authentification
- [ ] Inscription par email/password
- [ ] Connexion sécurisée (HTTPS)
- [ ] Réinitialisation mot de passe
- [ ] Validation email (optionnel MVP)

#### 2. Gestion des Tâches de Crawl
- [ ] **Créer une tâche** : saisir jusqu'à 25 URLs (textarea)
- [ ] **Lancer le crawl** : exécution asynchrone (Celery)
- [ ] **Voir le statut** : Pending → Running → Done → Error
- [ ] **Télécharger le CSV** : lien de téléchargement sécurisé
- [ ] **Historique** : liste des 50 dernières tâches

#### 3. Extraction de Données
**Données automatiquement extraites** (sans configuration) :
- `url` : URL de la page crawlée
- `title` : Balise `<title>`
- `h1` : Premier `<h1>` de la page
- `description` : Meta description
- `prices` : Détection automatique de prix (€, $, £)
- `links_count` : Nombre de liens sur la page
- `status_code` : Code HTTP (200, 404, etc.)
- `crawled_at` : Timestamp

**Format de sortie** : CSV UTF-8

#### 4. Respect des Règles
- [ ] **Respect robots.txt** : vérification automatique avant crawl
- [ ] **Délai entre requêtes** : 2 secondes minimum (CRAWL_DELAY)
- [ ] **Limite URLs** : Maximum 25 URLs par tâche
- [ ] **User-Agent identifiable** : "WebCrawler-SaaS/1.0"
- [ ] **Timeout** : 30 secondes par URL

#### 5. Interface Utilisateur
- [ ] **Dashboard** : vue d'ensemble des tâches
- [ ] **Statistiques** : nombre de tâches (pending, running, done, error)
- [ ] **Formulaire de création** : textarea pour URLs
- [ ] **Page détail tâche** : statut, résultats, erreurs
- [ ] **Design** : Bootstrap 5, responsive

#### 6. Stockage et Sécurité
- [ ] **Fichiers CSV** : stockés dans `/media/results/`
- [ ] **Rétention** : 30 jours, suppression automatique
- [ ] **Isolation** : chaque utilisateur voit uniquement ses tâches
- [ ] **Chiffrement** : HTTPS obligatoire
- [ ] **Logs** : toutes les tâches loggées (IP, date, URLs)

---

### 🎁 SHOULD HAVE (Souhaitable pour le MVP)

#### 7. Sélecteurs CSS Personnalisés (Phase 4)
- [ ] Interface drag & drop (ou formulaire simple)
- [ ] Définir des sélecteurs CSS custom : `.price`, `#title`, etc.
- [ ] Prévisualisation (optionnel)
- [ ] Templates pré-configurés (Amazon, Shopify, WooCommerce)

#### 8. Notifications
- [ ] Email quand tâche terminée
- [ ] Email en cas d'erreur

#### 9. API REST
- [ ] `POST /api/tasks/` : créer une tâche
- [ ] `GET /api/tasks/` : liste des tâches
- [ ] `GET /api/task/{id}/` : détails d'une tâche
- [ ] Authentification par token (optionnel MVP)

---

### 💡 COULD HAVE (Améliorations futures)

#### 10. Automatisation
- [ ] Planification récurrente (daily, weekly)
- [ ] Webhooks pour notifications
- [ ] Export multi-formats (JSON, Excel)

#### 11. Analytics
- [ ] Graphiques d'évolution des prix
- [ ] Alertes si prix change de >10%
- [ ] Comparaison multi-sites

#### 12. Collaboration
- [ ] Partage de tâches entre utilisateurs
- [ ] Export vers Google Sheets

---

### 🚫 WON'T HAVE (Hors scope MVP)

- ❌ Crawl de sites nécessitant login
- ❌ Gestion de JavaScript dynamique (Selenium)
- ❌ Proxies rotatifs
- ❌ Contournement de captchas
- ❌ Crawl de plus de 25 URLs par tâche
- ❌ Mobile app native

---

## 🎨 Maquettes Interface

### 1. Page d'Accueil (Non-Connecté)

```
╔════════════════════════════════════════════════╗
║  🕷️ WebCrawler SaaS        [Connexion] [S'inscrire] ║
╠════════════════════════════════════════════════╣
║                                                ║
║    Extrayez des données web sans coder        ║
║                                                ║
║    [Essayer Gratuitement - 3 crawls offerts]  ║
║                                                ║
║  ✅ No-code  🇫🇷 Français  🔒 RGPD  ⚡ Rapide   ║
║                                                ║
╚════════════════════════════════════════════════╝
```

### 2. Dashboard (Connecté)

```
╔════════════════════════════════════════════════╗
║  Dashboard - Marc                    [Déconnexion] ║
╠════════════════════════════════════════════════╣
║                                                ║
║  📊 Statistiques                               ║
║  ⏳ En attente: 2  |  ⚙️ En cours: 1           ║
║  ✅ Terminées: 15  |  ❌ Erreurs: 1            ║
║                                                ║
║  🚀 Créer une tâche                            ║
║  ┌────────────────────────────────────────┐  ║
║  │ URLs (une par ligne, max 25):          │  ║
║  │ https://example.com/produit1           │  ║
║  │ https://example.com/produit2           │  ║
║  └────────────────────────────────────────┘  ║
║          [Lancer le crawl]                    ║
║                                                ║
║  📋 Mes tâches                                 ║
║  ┌────┬────────┬────────┬──────────────────┐ ║
║  │ ID │ Statut │ URLs   │ Date             │ ║
║  ├────┼────────┼────────┼──────────────────┤ ║
║  │ 42 │ ✅ Done │ 10     │ 13/11 14:30    │💾│ ║
║  │ 41 │ ⚙️ Run  │ 5      │ 13/11 14:25    │ - │ ║
║  └────┴────────┴────────┴──────────────────┘ ║
╚════════════════════════════════════════════════╝
```

### 3. Détail d'une Tâche

```
╔════════════════════════════════════════════════╗
║  Tâche #42                      [← Retour]    ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Statut: ✅ Terminé                            ║
║  Créée le: 13/11/2025 14:30                   ║
║  Durée: 45 secondes                            ║
║  URLs: 10 | Items scrapés: 10                 ║
║                                                ║
║  [💾 Télécharger le CSV]                       ║
║                                                ║
║  🔗 URLs crawlées:                             ║
║  1. https://example.com/produit1 ✅           ║
║  2. https://example.com/produit2 ✅           ║
║  3. https://example.com/produit3 ✅           ║
║  ...                                           ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

## 📊 Structure des Données

### Modèle `CrawlTask`

```python
class CrawlTask:
    id: int                      # ID unique
    user: ForeignKey(User)       # Propriétaire
    urls: TextField              # URLs séparées par \n
    urls_count: int              # Nombre d'URLs
    status: CharField            # pending|running|done|error
    result_file: FileField       # Chemin vers CSV
    error_message: TextField     # Message d'erreur si échec
    created_at: DateTime         # Date de création
    updated_at: DateTime         # Dernière mise à jour
    completed_at: DateTime       # Date de fin
    items_scraped: int           # Nombre d'items extraits
    celery_task_id: CharField    # ID Celery pour tracking
```

### Format CSV de Sortie

```csv
url,title,h1,description,prices,links_count,status_code,crawled_at
https://example.com/produit1,"Produit 1","Titre H1","Description meta","29.99 €",45,200,2025-11-13T14:30:00Z
https://example.com/produit2,"Produit 2","Titre H2","Description 2","39.99 €",52,200,2025-11-13T14:30:02Z
```

---

## 🔄 Flux Utilisateur Principal

### Scénario : "Marc veut crawler 10 produits concurrents"

```
1. Marc s'inscrit sur webcrawler-saas.fr
   ↓
2. Vérifie son email (optionnel MVP)
   ↓
3. Se connecte au dashboard
   ↓
4. Colle 10 URLs dans le formulaire
   ↓
5. Clique sur "Lancer le crawl"
   ↓
6. Voit le statut "En cours" (⚙️)
   ↓
7. Reçoit un email "Crawl terminé" (optionnel MVP)
   ↓
8. Retourne sur le dashboard
   ↓
9. Clique sur "Télécharger CSV" (💾)
   ↓
10. Ouvre le CSV dans Excel
    ↓
11. Analyse les prix et prend des décisions
```

**Temps total estimé** : 5 minutes (dont 2 min de crawl)

---

## 🏗️ Architecture Technique

### Stack Technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Django | 5.1+ |
| API | Django REST Framework | 3.14+ |
| Crawler | Scrapy | 2.11+ |
| Queue | Celery | 5.3+ |
| Broker | Redis | 7.0+ |
| Database | PostgreSQL | 15+ (SQLite pour dev) |
| Frontend | Bootstrap | 5.3 |
| Containerisation | Docker | 24+ |
| Hébergement | VPS France | OVH/Scaleway |

### Schéma d'Architecture

```
┌─────────────┐
│  Utilisateur│
│   (Browser) │
└──────┬──────┘
       │ HTTPS
       ↓
┌──────────────────┐
│   Nginx (Proxy)  │
│   + Let's Encrypt│
└────────┬─────────┘
         │
         ↓
┌──────────────────┐      ┌─────────────┐
│  Django          │←────→│ PostgreSQL  │
│  (Web App)       │      │   (DB)      │
└────────┬─────────┘      └─────────────┘
         │
         │ Enqueue task
         ↓
┌──────────────────┐      ┌─────────────┐
│  Redis           │←────→│ Celery      │
│  (Broker)        │      │  Worker     │
└──────────────────┘      └──────┬──────┘
                                 │
                                 │ Execute
                                 ↓
                          ┌──────────────┐
                          │   Scrapy     │
                          │   Spider     │
                          └──────┬───────┘
                                 │
                                 │ HTTP Requests
                                 ↓
                          ┌──────────────┐
                          │  Sites Web   │
                          │  (Targets)   │
                          └──────────────┘
```

---

## 🔒 Sécurité et Limites

### Limites Techniques

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| Max URLs/tâche | 25 | Anti-abus, performance |
| Délai entre requêtes | 2 secondes | Respect serveurs cibles |
| Timeout par URL | 30 secondes | Éviter blocages |
| Taille max CSV | 50 MB | Stockage |
| Rétention fichiers | 30 jours | RGPD, coûts |
| Max tâches simultanées | 5 par user | Performance |

### Mesures de Sécurité

1. **Authentification**
   - Mots de passe hashés (bcrypt)
   - HTTPS obligatoire
   - Protection CSRF
   - Rate limiting sur login (5 tentatives/5 min)

2. **Isolation**
   - Chaque user voit uniquement ses tâches
   - Conteneurs Docker isolés pour les workers
   - Permissions strictes sur fichiers CSV

3. **Monitoring**
   - Logs de toutes les tâches (IP, date, URLs)
   - Alertes si >100 tâches/jour par user
   - Blocage automatique si abus détecté

4. **RGPD**
   - Données minimales (email, password)
   - Droit à l'oubli (suppression compte)
   - Exportation des données
   - Consentement explicite

---

## 💰 Modèle Économique

### Tarification

| Plan | Prix | Crawls/mois | URLs/tâche | Support |
|------|------|-------------|------------|---------|
| **Gratuit** | 0€ | 3 | 10 | Email |
| **Early Adopter** | 40€/mois | Illimité | 25 | Email prioritaire |
| **Standard** | 50€/mois | Illimité | 25 | Email + Chat |

### Coûts Estimés

**Mois 1-3 (≤30 users)**
- VPS-2 (2 vCPU, 4GB RAM) : 10€/mois
- Stockage S3/MinIO : 5€/mois
- Nom de domaine : 10€/an
- **Total** : ~16€/mois

**Mois 4+ (>30 users)**
- VPS-6 (6 vCPU, 16GB RAM) : 40€/mois
- Stockage : 10€/mois
- **Total** : ~50€/mois

### Rentabilité

**Avec 10 utilisateurs à 50€/mois** :
- CA : 500€/mois = 6 000€/an
- Charges (22%) : 1 320€/an
- Coûts hébergement : 200€/an
- **Bénéfice net** : ~4 480€/an

**Avec 50 utilisateurs à 50€/mois** :
- CA : 2 500€/mois = 30 000€/an
- Charges (22%) : 6 600€/an
- Coûts hébergement : 600€/an
- **Bénéfice net** : ~22 800€/an

---

## 📅 Planning MVP (12 Semaines)

| Semaine | Phase | Livrables |
|---------|-------|-----------|
| **S1** | Spécifications | Ce document, maquettes |
| **S2** | Django base | Projet + modèles |
| **S3** | API CRUD | Endpoints fonctionnels |
| **S4** | Scrapy | Spider basique + robots.txt |
| **S5** | Celery | Intégration asynchrone |
| **S6** | Interface | Dashboard + formulaires |
| **S7** | Sélecteurs CSS | Interface no-code |
| **S8** | Docker | Containerisation |
| **S9** | Déploiement | VPS en production |
| **S10** | Tests | Corrections bugs |
| **S11** | UX | Améliorations interface |
| **S12** | Lancement | Mise en ligne officielle |

---

## ✅ Critères de Succès MVP

Le MVP sera considéré comme réussi si :

### Critères Techniques
- [ ] Un utilisateur peut s'inscrire et se connecter
- [ ] Un utilisateur peut crawler 25 URLs en <3 minutes
- [ ] Les fichiers CSV sont téléchargeables
- [ ] Le respect de robots.txt est vérifié
- [ ] 95% de disponibilité (uptime)
- [ ] Aucune fuite de données entre utilisateurs

### Critères Business
- [ ] 10 utilisateurs actifs dans les 30 premiers jours
- [ ] 3 utilisateurs payants (Early Adopter) dans les 60 jours
- [ ] NPS (Net Promoter Score) ≥ 7/10
- [ ] <5% de taux de churn mensuel
- [ ] Coûts d'hébergement <20% du CA

### Critères UX
- [ ] Temps moyen de première tâche <5 minutes
- [ ] Taux de complétion d'inscription >80%
- [ ] Satisfaction utilisateur ≥4/5
- [ ] <3 tickets support/semaine

---

## 🚧 Risques et Mitigation

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Blocage par sites cibles | Élevé | Moyenne | User-Agent identifiable, respect robots.txt, délais |
| Abus utilisateurs (spam) | Élevé | Faible | Limites techniques, monitoring, logs |
| Surcharge serveur | Moyen | Moyenne | Scaling manuel VPS, queue Celery |
| Bugs crawler | Moyen | Élevée | Tests unitaires, logs détaillés |
| Non-conformité RGPD | Élevé | Faible | CGU claires, données minimales |
| Coûts imprévus | Moyen | Faible | Monitoring coûts, alertes |

---

## 📚 Documentation Utilisateur

### Guide de Démarrage Rapide (5 min)

1. **Inscrivez-vous** sur webcrawler-saas.fr
2. **Collez vos URLs** (max 25, une par ligne)
3. **Cliquez sur "Lancer"**
4. **Attendez 2-3 minutes**
5. **Téléchargez votre CSV**

### FAQ

**Q : Puis-je crawler n'importe quel site ?**
R : Non, vous devez respecter les robots.txt et avoir l'autorisation du propriétaire.

**Q : Combien de temps prend un crawl ?**
R : ~2 secondes par URL, soit ~50 secondes pour 25 URLs.

**Q : Les données sont-elles conservées ?**
R : Oui, 30 jours puis suppression automatique.

**Q : Puis-je crawler des sites avec login ?**
R : Non, pas dans le MVP. Prévu pour v2.

---

## 🎯 Prochaines Étapes (Post-MVP)

### Version 1.1 (Mois 2-3)
- Sélecteurs CSS personnalisés avancés
- Emails de notification
- Templates pré-configurés (Amazon, Shopify)

### Version 1.2 (Mois 4-6)
- Planification automatique (daily, weekly)
- Export JSON et Excel
- Webhooks

### Version 2.0 (Mois 7-12)
- Crawl avec JavaScript (Selenium)
- Comparateur de prix visuel
- Mobile app

---

**Validé par** : Thumser Luc  
**Date** : 13/11/2025  
**Version** : 1.0

---

*Ce document est vivant et sera mis à jour selon les retours utilisateurs et l'évolution du projet.*