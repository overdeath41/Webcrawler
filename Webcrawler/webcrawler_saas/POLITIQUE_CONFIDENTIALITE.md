# Politique de Confidentialité
## WebCrawler SaaS - Conformité RGPD

**Date d'entrée en vigueur : 13 novembre 2025**

---

## 1. Introduction

La protection de vos données personnelles est une priorité pour WebCrawler SaaS. Cette Politique de Confidentialité explique comment nous collectons, utilisons, conservons et protégeons vos données conformément au Règlement Général sur la Protection des Données (RGPD - UE 2016/679).

**Responsable du traitement :**  
Nom : Thumser Luc  
Statut : Auto-Entrepreneur  
Email : [votre-email@domaine.com]  
Adresse : [Votre adresse]

---

## 2. Données Collectées

### 2.1 Données d'Identification

Nous collectons uniquement les données strictement nécessaires au fonctionnement du Service :

| Donnée | Finalité | Base légale |
|--------|----------|-------------|
| Adresse email | Authentification, communication | Contrat |
| Mot de passe (hashé) | Sécurité du compte | Contrat |
| Date de création du compte | Gestion administrative | Contrat |

### 2.2 Données de Navigation

| Donnée | Finalité | Base légale |
|--------|----------|-------------|
| Logs de connexion (IP, date) | Sécurité, détection d'abus | Intérêt légitime |
| Historique des tâches de crawl | Fourniture du service | Contrat |
| URLs crawlées | Exécution des tâches | Contrat |

### 2.3 Données Extraites

Les fichiers CSV générés par vos tâches de crawl sont :
- **Stockés temporairement** sur nos serveurs (30 jours maximum)
- **Accessibles uniquement par vous**
- **Automatiquement supprimés** après 30 jours
- **Jamais analysés ou exploités** par nos services

⚠️ **Important** : Vous êtes responsable de la conformité RGPD des données que vous extrayez. Ne crawlez pas de données personnelles sans base légale valide.

---

## 3. Utilisation des Données

### 3.1 Finalités

Vos données sont utilisées uniquement pour :

1. **Fournir le Service** : authentification, exécution des crawls, stockage des résultats
2. **Améliorer le Service** : analyse anonymisée des performances, correction de bugs
3. **Communication** : emails de service (confirmation, alertes, mises à jour importantes)
4. **Sécurité** : détection d'abus, prévention de la fraude

### 3.2 Ce que nous NE faisons PAS

❌ Nous ne vendons JAMAIS vos données à des tiers  
❌ Nous ne partageons pas vos données avec des partenaires marketing  
❌ Nous n'utilisons pas vos données à des fins publicitaires  
❌ Nous n'analysons pas le contenu de vos fichiers CSV  

---

## 4. Partage des Données

### 4.1 Destinataires

Vos données peuvent être partagées uniquement avec :

| Destinataire | Finalité | Type de données |
|--------------|----------|-----------------|
| Hébergeur (ex: OVH, Scaleway) | Infrastructure technique | Toutes données |
| Stripe | Traitement des paiements | Email, montant |
| Vous-même | Export de vos données | Toutes vos données |

### 4.2 Transferts Hors UE

**Principe** : Vos données restent dans l'Union Européenne (hébergement France).

Si des transferts hors UE sont nécessaires (ex: services cloud), nous garantissons des clauses contractuelles types conformes au RGPD.

---

## 5. Conservation des Données

| Type de donnée | Durée de conservation | Justification |
|----------------|----------------------|---------------|
| Compte actif | Tant que le compte existe | Fourniture du service |
| Fichiers CSV | 30 jours maximum | Stockage temporaire |
| Logs de connexion | 12 mois | Sécurité, détection d'abus |
| Compte supprimé | Suppression sous 30 jours | Obligations légales |

**Après suppression de votre compte :**
- Toutes vos données personnelles sont supprimées définitivement sous 30 jours
- Seules les données anonymisées (statistiques globales) peuvent être conservées

---

## 6. Vos Droits RGPD

Conformément au RGPD, vous disposez des droits suivants :

### 6.1 Droit d'Accès (Art. 15)
Vous pouvez obtenir une copie de toutes vos données personnelles.

**Comment ?** Email à [votre-email@domaine.com] avec objet "Droit d'accès RGPD"

### 6.2 Droit de Rectification (Art. 16)
Vous pouvez corriger vos données inexactes ou incomplètes.

**Comment ?** Depuis votre compte ou par email

### 6.3 Droit à l'Effacement / "Droit à l'oubli" (Art. 17)
Vous pouvez demander la suppression de vos données.

**Comment ?** Email à [votre-email@domaine.com] avec objet "Suppression compte RGPD"

### 6.4 Droit à la Limitation du Traitement (Art. 18)
Vous pouvez demander le gel temporaire de vos données.

### 6.5 Droit à la Portabilité (Art. 20)
Vous pouvez récupérer vos données dans un format structuré (JSON, CSV).

**Comment ?** Email à [votre-email@domaine.com] avec objet "Portabilité données RGPD"

### 6.6 Droit d'Opposition (Art. 21)
Vous pouvez vous opposer au traitement de vos données pour motif légitime.

### 6.7 Droit de Retirer le Consentement
Si un traitement est basé sur votre consentement, vous pouvez le retirer à tout moment.

### 6.8 Droit d'Introduire une Réclamation
Vous pouvez déposer une plainte auprès de la CNIL (Commission Nationale de l'Informatique et des Libertés) :

**CNIL**  
3 Place de Fontenoy  
TSA 80715  
75334 Paris Cedex 07  
Tél : 01 53 73 22 22  
Site : [www.cnil.fr](https://www.cnil.fr)

---

## 7. Sécurité des Données

### 7.1 Mesures Techniques

Nous mettons en œuvre les mesures suivantes pour protéger vos données :

- ✅ **Chiffrement HTTPS** pour toutes les communications
- ✅ **Mots de passe hashés** avec algorithme bcrypt
- ✅ **Isolation des utilisateurs** : chaque utilisateur accède uniquement à ses données
- ✅ **Logs sécurisés** avec accès restreint
- ✅ **Sauvegardes régulières** chiffrées
- ✅ **Conteneurs Docker isolés** pour l'exécution des crawls
- ✅ **Rate limiting** pour prévenir les abus

### 7.2 Mesures Organisationnelles

- 🔒 Accès restreint aux données (développeur uniquement)
- 🔒 Procédures de détection et réponse aux incidents
- 🔒 Sensibilisation à la sécurité

### 7.3 En Cas de Violation

En cas de violation de données personnelles, nous nous engageons à :
1. Notifier la CNIL sous 72 heures
2. Vous informer si vos données sont concernées
3. Prendre toutes les mesures nécessaires pour limiter l'impact

---

## 8. Cookies et Traceurs

### 8.1 Cookies Utilisés

| Nom | Type | Finalité | Durée |
|-----|------|----------|-------|
| sessionid | Essentiel | Maintien de la session | Session |
| csrftoken | Essentiel | Protection CSRF | 1 an |

### 8.2 Consentement

Les cookies essentiels ne nécessitent pas de consentement. Aucun cookie publicitaire ou de tracking n'est utilisé.

---

## 9. Sous-Traitants

Nous travaillons avec les sous-traitants suivants :

| Sous-traitant | Service | Localisation | Conformité RGPD |
|---------------|---------|--------------|-----------------|
| [Hébergeur] | Infrastructure | France/UE | ✅ Conforme |
| Stripe | Paiements | UE | ✅ Conforme |

Tous nos sous-traitants sont contractuellement tenus de respecter le RGPD.

---

## 10. Mineurs

Le Service n'est pas destiné aux personnes de moins de 16 ans. Nous ne collectons pas sciemment de données de mineurs.

Si vous êtes parent et découvrez que votre enfant a créé un compte, contactez-nous pour suppression immédiate.

---

## 11. Modifications de la Politique

Cette Politique de Confidentialité peut être modifiée pour refléter les évolutions légales ou du Service.

En cas de modification importante :
- Notification par email 30 jours avant l'entrée en vigueur
- Possibilité de supprimer votre compte si vous refusez les modifications

Dernière version toujours disponible sur : [votre-site.com/confidentialite]

---

## 12. Contact - Délégué à la Protection des Données (DPO)

Pour toute question concernant vos données personnelles :

**Email :** [votre-email@domaine.com]  
**Objet :** "RGPD - [Votre demande]"  

Nous nous engageons à répondre sous 30 jours maximum (1 mois conformément au RGPD).

---

## 13. Base Légale des Traitements

| Traitement | Base légale RGPD |
|------------|------------------|
| Création et gestion du compte | Contrat (Art. 6.1.b) |
| Exécution des crawls | Contrat (Art. 6.1.b) |
| Détection d'abus | Intérêt légitime (Art. 6.1.f) |
| Emails de service | Contrat (Art. 6.1.b) |
| Conservation des logs | Obligation légale (Art. 6.1.c) |

---

**En utilisant WebCrawler SaaS, vous reconnaissez avoir lu et compris cette Politique de Confidentialité.**

---

*Dernière mise à jour : 13 novembre 2025*  
*Version : 1.0*