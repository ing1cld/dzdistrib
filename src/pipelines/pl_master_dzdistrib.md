# Pipeline `pl_master_dzdistrib` : orchestration quotidienne

## Paramètres
| Nom | Valeur par défaut | Rôle |
|---|---|---|
| `DateTraitement` | (vide) | Date du lot (vide = date du jour) |
| `RepoPath` | `ing1cld/dzdistrib/main` | Chemin du dépôt public ; transmis au pipeline d'ingestion |

## Chaîne d'activités (chaque lien : « En cas de réussite »)
```
1. Set variable `jour`
2. Invoke pipeline  -> pl_ingest_dzdistrib   (DateTraitement = @variables('jour'), RepoPath = @pipeline().parameters.RepoPath, attendre la fin)
3. Notebook         -> nb01_bronze           (DATE_TRAITEMENT = @variables('jour'), BATCH_ID = @pipeline().RunId)
4. Notebook         -> nb02_silver
5. Notebook         -> nb03_gold
6. Semantic model refresh -> sm_dzdistrib
```
Chaque activité 2 à 6 a un lien **En cas d'échec** vers une activité Teams ou Outlook :
`Échec de @{pipeline().Pipeline}, étape <nom de l'étape>, exécution @{pipeline().RunId}`.

## Réglages
- Notebooks : nouvelles tentatives = 1, délai d'expiration = 30 minutes.
- Invoke pipeline : nouvelles tentatives = 2.
- Paramètres de notebook : dans l'onglet **Paramètres** de l'activité, section des paramètres de base, ajouter `DATE_TRAITEMENT` (chaîne) et `BATCH_ID` (chaîne). Dans le notebook, la première cellule doit être définie comme **cellule de paramètres**.

## Planification
- **Dev** : aucune planification.
- **Test** : exécution manuelle pendant la recette.
- **Prod** : bouton **Planifier**, tous les jours à 05h00 (fuseau horaire Algérie), dates de début et de fin renseignées.

## Test d'idempotence
Lancer le pipeline deux fois de suite avec la même `DateTraitement` : les volumes de `silver_*` et `gold_*` ne doivent pas changer.
