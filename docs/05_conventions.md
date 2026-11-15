# Conventions

## Éléments Fabric
| Type | Préfixe | Exemple |
|---|---|---|
| Espace de travail | `ws-<projet>-<env>` | `ws-dzdistrib-prod` |
| Lakehouse | `lh_<couche>` | `lh_silver` |
| Pipeline | `pl_<usage>_<projet>` | `pl_ingest_dzdistrib` |
| Notebook | `nbNN_<couche>` | `nb02_silver` |
| Dataflow Gen2 | `df_<usage>` | `df_objectifs_excel` |
| Modèle sémantique | `sm_<projet>` | `sm_dzdistrib` |
| Rapport | `rpt_<projet>_<sujet>` | `rpt_dzdistrib_direction` |
| Pipeline de déploiement | `dp_<projet>` | `dp_dzdistrib` |

## Tables et colonnes
- Tables : `bronze_<entité>`, `silver_<entité>`, `gold_dim_<entité>`, `gold_fact_<processus>`, `meta_<usage>`.
- Colonnes : minuscules, mots séparés par des tirets bas, sans accents ni espaces.
- Colonnes techniques : préfixe tiret bas (`_source_file`, `_batch_id`, `_ingestion_ts`).
- Dates au format ISO `AAAA-MM-JJ`.

## Git
- Branches : `main` (validée), `dev` (intégration), `feature/<sujet>` (travail en cours).
- Commits : `feat:`, `fix:`, `docs:`, `refactor:`, `test:` suivi d'une description courte.
- Une demande de fusion (pull request) relue par un collègue avant fusion dans `main`.

## Code
- Un bloc de code par type de problème (types, doublons, formats, validation) pour localiser vite une erreur.
- Contrôles bloquants (`assert`) pour arrêter le notebook plutôt que publier une donnée fausse.
- Aucun secret en clair, aucun identifiant d'espace de travail en dur.
