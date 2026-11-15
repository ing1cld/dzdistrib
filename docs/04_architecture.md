# Architecture cible

## 1. Vue d'ensemble

```
SOURCES                      EXTRACTION              STOCKAGE (OneLake)                           SERVICE
ERP (CSV)      ─┐
CRM (CSV)      ─┤  pl_ingest_dzdistrib     lh_bronze            lh_silver            lh_gold            sm_dzdistrib (Direct Lake)
Référentiels   ─┤  Copy data (HTTP)   ──►  Files/landing   ──►  silver_* + rejets ──► étoile gold_*  ──► mesures DAX, RLS
Objectifs      ─┘  vers Files/landing      bronze_* (texte)    (nb02_silver)         (nb03_gold)         rpt_dzdistrib_direction
                                            (nb01_bronze)                                                rpt_dzdistrib_sante
                              Orchestration : pl_master_dzdistrib (planifié 05h00, alertes d'échec)
```

## 2. Espaces de travail et environnements

| Environnement | Espace de travail | Rôle | Données | Planification | Accès en écriture |
|---|---|---|---|---|---|
| Dev | `ws-dzdistrib-dev` | Développement, essais, connecté à Git (branche `dev`) | Jeu complet de test | Aucune (exécution manuelle) | Ingénieurs de données |
| Test | `ws-dzdistrib-test` | Recette avec le métier | Même jeu, chargé par pipeline | Manuelle pendant la recette | Pipeline de déploiement et administrateurs |
| Prod | `ws-dzdistrib-prod` | Service aux décideurs | Données réelles à terme | Tous les jours à 05h00 | Pipeline de déploiement uniquement |

Les trois espaces contiennent **les mêmes éléments avec les mêmes noms**. Ce qui change d'un environnement à l'autre :
la capacité, les accès, la planification, et la connexion aux sources. Les notebooks n'écrivent aucun identifiant en dur :
ils lisent l'espace de travail courant (`notebookutils.runtime.context`), ce qui les rend identiques partout.

Option « grande organisation » : séparer les espaces techniques (`ws-dzdistrib-data-<env>`) des espaces BI (`ws-dzdistrib-bi-<env>`) :
les utilisateurs métier n'ont alors jamais accès aux Lakehouses.

## 3. Contenu d'un espace de travail (organisé en dossiers)

```
ws-dzdistrib-<env>
├── 01_ingestion
│   ├── pipelines          pl_ingest_dzdistrib, pl_master_dzdistrib
│   └── dataflows          df_objectifs_excel (option Excel)
├── 02_stockage
│   ├── lh_bronze          fichiers bruts (Files/landing) et tables bronze_*
│   ├── lh_silver          tables silver_*, silver_rejets, meta_controles_qualite
│   └── lh_gold            tables gold_* (étoile, KPI, qualité)
├── 03_transformation
│   ├── nb01_bronze
│   ├── nb02_silver
│   └── nb03_gold
├── 04_semantique
│   └── sm_dzdistrib
├── 05_rapports
│   ├── rpt_dzdistrib_direction
│   └── rpt_dzdistrib_sante
└── 90_exploration         brouillons (jamais déployés en Prod)
```

## 4. Contenu des Lakehouses

| Lakehouse | Zone | Contenu |
|---|---|---|
| `lh_bronze` | Files/landing | `erp/AAAA/MM/JJ/ventes_erp.csv`, `crm/AAAA/MM/JJ/clients_crm.csv`, `referentiel/AAAA/MM/JJ/produits.csv`, `agences.csv`, `controle_gestion/AAAA/MM/JJ/objectifs.csv` |
| `lh_bronze` | Tables | `bronze_ventes`, `bronze_clients`, `bronze_produits`, `bronze_agences`, `bronze_objectifs` (tout en texte, plus `_source_file`, `_batch_id`, `_ingestion_ts`) |
| `lh_silver` | Tables | `silver_ventes`, `silver_clients`, `silver_produits`, `silver_agences`, `silver_objectifs`, `silver_rejets`, `meta_controles_qualite` |
| `lh_gold` | Tables | `gold_fact_ventes`, `gold_dim_date`, `gold_dim_client`, `gold_dim_produit`, `gold_dim_agence`, `gold_objectifs`, `gold_qualite_rejets`, `gold_kpi_agence_mois` |

Les trois Lakehouses sont créés **sans schémas**, dans le même espace de travail.

## 5. Sécurité

| Profil | Dev | Test | Prod | Lakehouses | Rapport |
|---|---|---|---|---|---|
| Ingénieur de données | Contributor | Viewer | Viewer | Tous (Dev) | Oui |
| Analyste BI | Contributor | Viewer | Aucun | Gold seulement | Oui |
| Responsable d'agence | Aucun | Aucun | Aucun | Aucun | Via application, filtre RLS par agence |
| Direction | Aucun | Aucun | Aucun | Aucun | Via application |
| Compte de service | Contributor | Contributor | Contributor | Selon besoin | Non |

Les droits sont donnés à des **groupes de sécurité**, pas à des personnes.

## 6. Décisions d'architecture

| Décision | Choix | Raison |
|---|---|---|
| Lakehouses | Un par couche | Droits distincts, responsabilités séparées |
| Lecture entre couches | Chemin OneLake complet construit avec l'identifiant de l'espace courant | Identique en Dev, Test et Prod |
| Ingestion | Pipeline avec Copy data en format binaire | Copie fidèle, sans interprétation du fichier |
| Bronze | Ajout par lot (`append`) avec identifiant de lot | Historique complet, relance sans doublon |
| Silver | Dernière version par clé, quarantaine des rejets | Données propres et rejets tracés |
| Gold | Étoile avec montants précalculés | Cohérence des chiffres, performance |
| Modèle sémantique | Direct Lake, un modèle certifié | Rapidité et source unique de vérité |
| Orchestration | Pipeline maître planifié, alertes d'échec | Fiabilité d'exploitation |
