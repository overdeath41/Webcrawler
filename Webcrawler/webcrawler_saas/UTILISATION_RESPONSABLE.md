# 🌱 Guide d'Utilisation Responsable
## WebCrawler SaaS - Éthique et Bonnes Pratiques

---

## 🎯 Notre Engagement Éthique

WebCrawler SaaS est conçu pour **faciliter l'accès aux données publiques** tout en respectant :
- 🌍 Les droits des propriétaires de sites web
- 🔒 La vie privée des individus  
- ⚖️ Les lois en vigueur (RGPD, droit d'auteur)
- 🤝 L'éthique du web scraping

---

## ✅ Utilisations Autorisées et Recommandées

### 1. 🏢 Votre Propre Site Web
**Cas d'usage** : Crawler votre site e-commerce pour vérifier les prix, surveiller la disponibilité des produits.

✅ **Totalement autorisé** - C'est votre contenu !

### 2. 📊 Données Publiques avec Autorisation
**Cas d'usage** : Extraire des données d'un site partenaire après accord écrit.

✅ **Autorisé avec preuve d'autorisation**

### 3. 🔍 Recherche et Analyse (Usage Privé)
**Cas d'usage** : Analyser des tendances de marché, veille concurrentielle pour usage interne.

✅ **Autorisé si respecte robots.txt et pas de revente**

### 4. 📈 Comparaison de Prix (Usage Personnel)
**Cas d'usage** : Comparer les prix de produits pour votre consommation personnelle.

✅ **Autorisé pour usage personnel uniquement**

### 5. 🎓 Projets Éducatifs
**Cas d'usage** : Apprendre le web scraping, projet d'école, formation.

✅ **Autorisé sur des sites de test ou avec faible volume**

---

## ❌ Utilisations INTERDITES

### 1. 🚫 Extraction de Données Personnelles
**Exemple** : Crawler des profils LinkedIn, Facebook pour récupérer emails, téléphones.

❌ **STRICTEMENT INTERDIT** - Violation RGPD  
⚖️ **Risque** : Amende jusqu'à 20M€ ou 4% du CA

### 2. 🚫 Concurrence Déloyale
**Exemple** : Copier massivement le catalogue d'un concurrent pour revente.

❌ **INTERDIT** - Violation droit d'auteur  
⚖️ **Risque** : Poursuites judiciaires

### 3. 🚫 Surcharge de Serveurs
**Exemple** : Crawler un site 1000 fois/minute pour le mettre hors ligne.

❌ **INTERDIT** - Attaque DDoS  
⚖️ **Risque** : Poursuites pénales

### 4. 🚫 Contournement de Protection
**Exemple** : Utiliser des proxies pour éviter les blocages, captchas.

❌ **INTERDIT** - Violation CGU des sites  
⚖️ **Risque** : Bannissement + poursuites

### 5. 🚫 Spam et Marketing Abusif
**Exemple** : Extraire des emails pour envoi massif non sollicité.

❌ **STRICTEMENT INTERDIT** - Violation RGPD  
⚖️ **Risque** : Amende CNIL + plaintes

---

## 📋 Checklist Avant de Crawler

Avant chaque crawl, posez-vous ces questions :

### ✓ Légalité
- [ ] Ai-je l'autorisation du propriétaire du site ?
- [ ] Les données sont-elles publiquement accessibles (sans login) ?
- [ ] Le site a-t-il un fichier robots.txt qui l'autorise ?
- [ ] Les données ne sont-elles PAS des données personnelles sensibles ?

### ✓ Éthique
- [ ] Mon crawl ne va-t-il pas surcharger le serveur cible ?
- [ ] Ai-je un délai raisonnable entre les requêtes (min 2 secondes) ?
- [ ] Mon usage est-il équitable (fair use) ?
- [ ] Vais-je créditer la source si je publie les données ?

### ✓ Technique
- [ ] Ai-je vérifié le fichier robots.txt du site ?
- [ ] Mon User-Agent est-il identifiable (pas anonyme) ?
- [ ] Le volume de données est-il raisonnable (<25 URLs) ?
- [ ] Ai-je un plan B si le site bloque mon crawl ?

---

## 🛡️ Protections Intégrées

Pour vous aider à crawler de manière responsable, WebCrawler SaaS impose automatiquement :

| Protection | Valeur | Pourquoi |
|------------|--------|----------|
| **Max URLs/tâche** | 25 URLs | Éviter surcharge serveurs |
| **Délai entre requêtes** | 2 secondes min | Respecter bande passante |
| **Respect robots.txt** | Obligatoire | Conformité légale |
| **Rate limiting** | Auto | Prévenir abus |
| **User-Agent identifiable** | Oui | Transparence |
| **Logs conservés** | 12 mois | Traçabilité |

⚠️ **Ces limites ne peuvent pas être contournées.**

---

## 📖 Comprendre robots.txt

### Qu'est-ce que robots.txt ?

C'est un fichier texte placé à la racine d'un site web qui indique aux robots (crawlers) quelles pages peuvent être crawlées.

**Exemple** : `https://example.com/robots.txt`

```
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
```

### Comment Lire robots.txt

| Directive | Signification | Action WebCrawler |
|-----------|---------------|-------------------|
| `User-agent: *` | S'applique à tous les robots | ✅ Nous respectons |
| `Disallow: /admin/` | Interdiction de crawler /admin/ | ❌ Bloqué automatiquement |
| `Allow: /public/` | Autorisation explicite | ✅ Autorisé |
| `Crawl-delay: 5` | Attendre 5 sec entre requêtes | ✅ Respecté (min 2 sec) |

### Vérifier robots.txt

Avant de crawler, visitez :
```
https://[site-cible]/robots.txt
```

Si le fichier n'existe pas → **Prudence**, demander l'autorisation reste recommandé.

---

## 🎓 Cas d'Usage Concrets

### ✅ CAS 1 : Monitoring de Prix E-Commerce

**Contexte** : Vous êtes e-commerçant et voulez surveiller vos propres prix.

```
✅ Légal : Votre site = vos données
✅ Éthique : Usage légitime
✅ Fréquence : 1x/jour suffisant
```

**Recommandation** : Crawler votre site en dehors des heures de pointe.

---

### ✅ CAS 2 : Veille Concurrentielle (Usage Interne)

**Contexte** : Analyser les prix de 3 concurrents pour ajuster votre stratégie.

```
✅ Légal : Données publiques, usage privé
✅ Éthique : Pas de revente, faible volume
⚠️ Vérifier robots.txt de chaque site
```

**Recommandation** : 1x/semaine max, 5-10 URLs par site.

---

### ❌ CAS 3 : Extraction Massive pour Revente

**Contexte** : Crawler 10 000 produits d'Amazon pour créer un site comparateur commercial.

```
❌ Illégal : Violation CGU Amazon
❌ Non-éthique : Concurrence déloyale
❌ Risque : Poursuites juridiques + compte banni
```

**Alternative légale** : Utiliser l'API officielle Amazon Product Advertising API.

---

### ❌ CAS 4 : Collecte d'Emails pour Newsletter

**Contexte** : Extraire emails depuis un annuaire professionnel pour envoyer une newsletter.

```
❌ Illégal : Violation RGPD (pas de consentement)
❌ Risque : Amende CNIL jusqu'à 20M€
```

**Alternative légale** : Formulaires d'inscription avec consentement explicite.

---

## 🔍 Alternatives Légales au Web Scraping

Avant de crawler, vérifiez si ces alternatives existent :

| Besoin | Alternative Légale |
|--------|-------------------|
| Données produits | **API officielle** (Amazon, eBay, etc.) |
| Données financières | **API Yahoo Finance, Alpha Vantage** |
| Données publiques | **Open Data gouvernementaux** |
| Réseaux sociaux | **API officielles** (Twitter API, LinkedIn API) |
| Informations entreprises | **API Infogreffe, Pappers** |

---

## 📞 En Cas de Doute

Si vous n'êtes pas sûr de la légalité de votre crawl :

1. **Consultez les CGU du site cible**
2. **Vérifiez le fichier robots.txt**
3. **Contactez le propriétaire du site** (email souvent dans mentions légales)
4. **Consultez un juriste** spécialisé en droit numérique
5. **Contactez-nous** : [votre-email@domaine.com]

---

## ⚖️ Cadre Juridique (France)

### Lois Applicables

| Loi | Domaine | Impact |
|-----|---------|--------|
| **RGPD** | Données personnelles | Protection vie privée |
| **Code Pénal Art. 323-1** | Accès frauduleux | Piratage = prison |
| **Code de la Propriété Intellectuelle** | Droit d'auteur | Protection contenus |
| **Loi pour une République Numérique** | Données ouvertes | Open Data public |

### Jurisprudence Notable

- **Ryanair c. PR Aviation (2015)** : Scraping autorisé si données publiques et pas de surcharge serveur
- **LinkedIn c. hiQ Labs (2019)** : Scraping de données publiques autorisé (USA)
- **CNIL (2020)** : Scraping d'emails = violation RGPD

---

## 🌟 Nos Valeurs

WebCrawler SaaS s'engage à :

- 🇫🇷 **Hébergement France** : Données stockées en France (OVH, Scaleway)
- 🔒 **Transparence** : Aucune vente de données, logs accessibles
- ⚖️ **Conformité** : Respect RGPD, robots.txt, CGU
- 🤝 **Éthique** : Promotion du fair use, limites techniques
- 📚 **Éducation** : Guides, documentation, sensibilisation

---

## 📚 Ressources Complémentaires

### 📖 Documentation Officielle
- [Règlement RGPD (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [Guide CNIL - Web scraping](https://www.cnil.fr/)
- [Robots.txt Standard](https://www.robotstxt.org/)

### 🎓 Formations
- [MOOC CNIL - RGPD](https://www.cnil.fr/fr/mooc-latelier-rgpd)
- [Google - Directives pour les webmasters](https://developers.google.com/search/docs/advanced/guidelines/webmaster-guidelines)

### 👥 Communauté
- [Forum WebCrawler SaaS](https://forum.webcrawler-saas.fr) *(à créer)*
- [Discord](https://discord.gg/webcrawler) *(à créer)*

---

## ✉️ Contact

Pour toute question sur l'utilisation responsable :

**Email :** [votre-email@domaine.com]  
**Objet :** "Question Éthique"

Nous répondons sous 48h.

---

**⚡ Crawler, oui. Responsablement, toujours. ⚡**

---

*Dernière mise à jour : 13 novembre 2025*