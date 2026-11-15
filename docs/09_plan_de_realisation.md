# Plan de réalisation par jalons

Chaque jalon se termine par une **preuve** (chiffre ou capture) à comparer avec `07_recette.md`.

| Jalon | Travail | Preuve |
|---|---|---|
| **J0 Dépôt** | Publier les fichiers de `data_formation/` dans `ing1cld/dzdistrib` et vérifier leur accès HTTP anonyme (`data_formation/erp/ventes_erp.csv`) | Le CSV est accessible depuis la connexion Fabric configurée |
| **J1 Espace Dev** | Créer `ws-dzdistrib-dev`, les dossiers `01_` à `05_` et `90_`, les Lakehouses `lh_bronze`, `lh_silver`, `lh_gold` (sans schémas) | Arborescence conforme à `04_architecture.md` |
| **J2 Ingestion** | Créer la connexion HTTP, le pipeline `pl_ingest_dzdistrib` (voir `src/pipelines/`), l'exécuter | 5 fichiers dans `lh_bronze` sous `Files/landing/.../AAAA/MM/JJ` |
| **J3 Bronze** | Notebook `nb01_bronze` (Lakehouse par défaut `lh_bronze`) | 12 210 / 308 / 40 / 5 / 120 lignes |
| **J4 Silver** | Notebook `nb02_silver` (Lakehouse par défaut `lh_silver`, lecture de `lh_bronze`) | 11 965 ventes, 165 rejets, 300 clients, taux 1,36 % |
| **J5 Gold** | Notebook `nb03_gold` (Lakehouse par défaut `lh_gold`, lecture de `lh_silver`) puis `tests/reconciliation.sql` sur le point de terminaison SQL de `lh_gold` | CA net 118 856 038,64 |
| **J6 Sémantique** | Modèle `sm_dzdistrib` en Direct Lake, relations, mesures DAX (sections 24 et 25 du guide), rapport en 3 pages, rôle RLS par agence | Valeurs de la recette, test du rôle |
| **J7 Orchestration** | Pipeline maître `pl_master_dzdistrib`, alertes d'échec, planification | Exécution complète réussie, relance sans doublon |
| **J8 Git** | Connecter `ws-dzdistrib-dev` à la branche `dev` (voir `08_alm_git_deploiement.md`) | Éléments présents dans `fabric/` |
| **J9 Test et Prod** | Créer `ws-dzdistrib-test` et `ws-dzdistrib-prod`, pipeline de déploiement `dp_dzdistrib`, déploiement, exécution et recette en Test, planification en Prod | Recette Test réussie, Prod planifiée |
| **J10 Options** | Dataflow Gen2 pour les objectifs en Excel ; Copy job incrémental depuis une base ; page « Santé des données » ; séparation des espaces data et BI | Selon l'option |
