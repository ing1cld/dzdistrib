# Cycle de vie : Git, environnements, déploiement

## Principe
- **Git** conserve l'historique et permet la relecture du code. Seul l'espace de travail **Dev** est connecté à Git.
- Le **pipeline de déploiement** `dp_dzdistrib` fait passer le contenu validé de Dev vers Test, puis Prod.
- On ne modifie **jamais** directement Test ou Prod.

## 1. Connecter Dev à Git
1. Utiliser le dépôt GitHub public `ing1cld/dzdistrib` (accès en lecture anonyme requis par la connexion HTTP d'ingestion) et y pousser les données de `data_formation/`.
2. Créer la branche `dev` si elle n'existe pas.
3. Dans `ws-dzdistrib-dev` : **Paramètres de l'espace de travail, Intégration Git**, choisir le fournisseur, se connecter, sélectionner le dépôt, la branche `dev` et le dossier contenant les définitions Fabric.
4. Premier **Synchroniser** : les éléments de l'espace de travail sont enregistrés dans le dossier `fabric/` du dépôt.
5. Au quotidien : modifier dans Fabric, puis **Valider (commit)** depuis le panneau Contrôle de code source avec un message clair. Pour récupérer des changements du dépôt : **Mettre à jour**.

> **Prérequis non satisfait dans ce dépôt :** `fabric/` ne contient actuellement que `.gitkeep`. Les notebooks Python et les guides de pipelines dans `src/` ne sont pas des définitions Fabric déployables. Exporter ou créer les éléments Fabric dans le format pris en charge avant de configurer la synchronisation Git et les déploiements.

## 2. Flux de travail
```
feature/<sujet>  ──►  dev  ──(demande de fusion relue)──►  main
                       │
                  espace Dev (Git)  ──►  Test  ──►  Prod   (pipeline de déploiement)
```
Pour un travail isolé, on peut créer une branche et un espace de travail temporaires (« Branch out to new workspace ») puis fusionner.

## 3. Pipeline de déploiement
1. Liste des espaces de travail : **Pipelines de déploiement**, **Créer un pipeline** `dp_dzdistrib`, trois étapes : Dev, Test, Prod.
2. Affecter `ws-dzdistrib-dev`, `ws-dzdistrib-test`, `ws-dzdistrib-prod` à chaque étape.
3. **Déployer** de Dev vers Test, puis de Test vers Prod, en lisant la liste des différences avant chaque déploiement.
4. **Règles de déploiement** : par étape, remplacer ce qui change d'un environnement à l'autre (par exemple la connexion à la source, ou le Lakehouse par défaut d'un notebook si le déploiement ne le rattache pas tout seul).

À savoir :
- Le déploiement transporte les **définitions** (notebooks, pipelines, modèles, rapports), pas le **contenu** des tables. Après un premier déploiement, on exécute les pipelines dans l'environnement cible pour remplir les Lakehouses.
- Selon les types d'éléments pris en charge par les pipelines de déploiement au moment où tu les utilises, il peut être nécessaire de créer à la main les trois Lakehouses (mêmes noms) dans Test et Prod avant le premier déploiement. Vérifier la liste des éléments pris en charge dans la documentation Fabric.
- Après chaque déploiement, vérifier que chaque notebook a bien comme Lakehouse par défaut celui du **même** environnement.

## 4. Liste de contrôle d'une mise en production
- [ ] Demande de fusion relue et fusionnée.
- [ ] Déploiement en Test, pipeline maître exécuté, recette `07_recette.md` réussie.
- [ ] Validation écrite du Directeur commercial pour les 3 KPI principaux.
- [ ] Plan de retour arrière prêt (commit précédent et `RESTORE` Delta).
- [ ] Déploiement en Prod, planification activée à 05h00, alertes testées.
- [ ] Communication aux utilisateurs (application Power BI, date de mise à disposition).

## 5. Retour arrière
1. Redéployer la version précédente depuis Git (commit de la dernière version stable) vers Dev, puis Test, puis Prod.
2. Restaurer les tables concernées : `RESTORE TABLE nom TO VERSION AS OF n`.
3. Relancer le pipeline et rejouer les contrôles de recette.
