# Ordre de mission : pilotage commercial DzDistrib

**Demandeur** : Direction commerciale, DzDistrib (distribution agroalimentaire, 5 agences : Béjaïa, Alger, Sétif, Oran, Constantine)
**Responsable côté métier** : Directeur commercial
**Responsable côté données** : Data engineer (toi)
**Date de mise en production souhaitée** : dans 4 semaines (avant le prochain comité de direction)

## Contexte
Les chiffres de ventes proviennent de l'ERP (exports CSV) et du CRM. Chaque service les agrège à sa manière, les totaux
diffèrent d'un rapport à l'autre et personne ne suit les objectifs par agence. Il n'existe aucune source unique de vérité.

## Besoin exprimé
Un tableau de bord mensuel pour le comité de direction : chiffre d'affaires, marge, retours, atteinte des objectifs par agence,
meilleurs produits et clients. Les chiffres doivent être fiables et se mettre à jour sans intervention manuelle.

## Livrables attendus
1. Plateforme de données Fabric : couches Bronze, Silver, Gold dans trois environnements (Dev, Test, Prod).
2. Ingestion automatisée depuis les sources (pipeline Fabric), planifiée chaque nuit à 05h00.
3. Modèle sémantique certifié `sm_dzdistrib` et rapport de direction en 3 pages, plus une page « Santé des données ».
4. Sécurité par lignes : un responsable d'agence ne voit que son agence.
5. Documentation : fiches KPI, contrats de données, architecture, runbook d'exploitation.
6. Dépôt Git, déploiement contrôlé Dev, Test, Prod.

## Critères d'acceptation
- Les valeurs de contrôle de `docs/07_recette.md` sont reproduites.
- Les lignes rejetées sont tracées avec leur motif et le taux de rejet est inférieur à 2 %.
- Le pipeline est idempotent (une relance ne crée aucun doublon) et alerte en cas d'échec.
- Le rapport est à jour à 07h00 chaque jour ouvré.

## Contraintes
- Données de test fictives. Aucune donnée personnelle n'est exposée dans la couche Gold.
- Un seul modèle sémantique officiel par sujet.
- Les secrets ne sont jamais stockés dans le code.
