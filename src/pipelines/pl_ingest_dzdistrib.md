# Pipeline `pl_ingest_dzdistrib` : extraction vers `lh_bronze`

**But** : copier chaque fichier source, tel quel, dans `Files/landing/<source>/AAAA/MM/JJ/` du Lakehouse `lh_bronze`.
**Méthode** : activité **Copy data** avec source HTTP et format **Binaire** (le fichier n'est ni lu ni interprété).

## Connexion à créer (une fois)
Paramètres (engrenage), **Gérer les connexions et les passerelles**, **Nouvelle connexion** :
- Type : **HTTP**
- URL de base : `https://raw.githubusercontent.com/`
- Authentification : **Anonyme uniquement si le dépôt est public** ; sinon, configurer une méthode d'authentification prise en charge par Fabric sans placer de secret dans le dépôt
- Nom : `cx_github_raw_dzdistrib`

## Paramètres du pipeline
| Nom | Type | Valeur par défaut | Rôle |
|---|---|---|---|
| `DateTraitement` | Chaîne | (vide) | Date du lot, `AAAA-MM-JJ`. Vide = date du jour |
| `RepoPath` | Chaîne | `ing1cld/dzdistrib/main` | Chemin dans GitHub (propriétaire, dépôt, branche) |
| `Sources` | Tableau | voir ci-dessous | Liste des fichiers à copier |

Valeur du paramètre `Sources` :
```json
[
  {"dossier": "erp",              "fichier": "ventes_erp.csv"},
  {"dossier": "crm",              "fichier": "clients_crm.csv"},
  {"dossier": "referentiel",      "fichier": "produits.csv"},
  {"dossier": "referentiel",      "fichier": "agences.csv"},
  {"dossier": "controle_gestion", "fichier": "objectifs.csv"}
]
```

## Activités
1. **Set variable** `jour` (variable de type Chaîne), valeur (contenu dynamique) :
   `@if(empty(pipeline().parameters.DateTraitement), formatDateTime(utcnow(), 'yyyy-MM-dd'), pipeline().parameters.DateTraitement)`
2. **ForEach** (après l'étape 1, en cas de réussite) :
   - Éléments : `@pipeline().parameters.Sources`
   - Séquentiel : non (traitement en parallèle, 5 maximum)
   - Dans la boucle : une activité **Copy data** :
     - **Source** : connexion `cx_github_raw_dzdistrib`, format **Binary**, URL relative :
       `@concat(pipeline().parameters.RepoPath, '/data_formation/', item().dossier, '/', item().fichier)`
     - **Destination** : Lakehouse `lh_bronze`, racine **Files**, format **Binary**, chemin de dossier :
       `@concat('landing/', item().dossier, '/', formatDateTime(variables('jour'), 'yyyy/MM/dd'))`,
       nom de fichier : `@item().fichier`
     - **Général** : nouvelles tentatives = 2, intervalle 30 secondes, délai d'expiration = 10 minutes.
3. **Activité de notification** en cas d'échec du ForEach (Teams ou Office 365 Outlook), message :
   `Échec de l'ingestion DzDistrib, lot @{variables('jour')}, pipeline @{pipeline().Pipeline}, exécution @{pipeline().RunId}`.

## Contrôle
Lakehouse `lh_bronze`, **Files**, `landing` : 5 fichiers rangés par source et par date du jour.
