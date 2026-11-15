# nb02_silver  |  Lakehouse par défaut : lh_silver
# Rôle : lire lh_bronze, nettoyer, valider, mettre les rejets en quarantaine, écrire dans lh_silver.

# %% [Cellule 1 : lire une table d'un autre Lakehouse du même espace de travail]
ctx = notebookutils.runtime.context
WS = ctx.get('currentWorkspaceId')       # fonctionne identiquement en Dev, Test et Prod
print('Espace de travail :', WS, '| Lakehouse par défaut :', ctx.get('defaultLakehouseName'))   # lh_silver

def lire(lakehouse, table):
    chemin = f'abfss://{WS}@onelake.dfs.fabric.microsoft.com/{lakehouse}.Lakehouse/Tables/{table}'
    return spark.read.format('delta').load(chemin)

# %% [Cellule 2 : outils communs]
from pyspark.sql import functions as F, Window

TECH = ['_source_file', '_batch_id', '_ingestion_ts']
MAP_WILAYA = {'bejaia': 'Béjaïa', 'alger': 'Alger', 'setif': 'Sétif', 'oran': 'Oran', 'constantine': 'Constantine'}
MAP_TYPE   = {'grossiste': 'Grossiste', 'detaillant': 'Détaillant', 'restaurant': 'Restaurant'}
MAP_STATUT = {'livree': 'Livrée', 'annulee': 'Annulée', 'retour': 'Retour'}
SEUIL_REJETS_PCT = 2.0

def norm(colname):
    # minuscules, sans espaces autour, sans accents (pour comparer)
    return F.translate(F.lower(F.trim(F.col(colname))), 'éèêëàâäîïôöùûüç', 'eeeeaaaiioouuuc')

def mapping(d):
    return F.create_map([F.lit(x) for kv in d.items() for x in kv])

def dernier(df, cles, *ordres_secondaires):
    # garde, par clé, la version la plus récemment ingérée (puis selon les ordres secondaires)
    w = Window.partitionBy(*cles).orderBy(F.col('_ingestion_ts').desc(), *ordres_secondaires)
    return df.withColumn('_rn', F.row_number().over(w)).filter('_rn = 1').drop('_rn')

def ecrire(df, nom):
    (df.write.format('delta').mode('overwrite').option('overwriteSchema', 'true').saveAsTable(nom))
    print(nom, ':', spark.table(nom).count(), 'lignes')

# %% [Cellule 3 : référentiels (clients, produits, agences, objectifs)]
silver_clients = (dernier(lire('lh_bronze', 'bronze_clients'), ['code_client'], F.col('date_creation').desc())
    .withColumn('code_client', F.upper(F.trim('code_client')))
    .withColumn('nom_client', F.initcap(F.trim('nom_client')))
    .withColumn('wilaya', mapping(MAP_WILAYA)[norm('wilaya')])
    .withColumn('type_client', mapping(MAP_TYPE)[norm('type_client')])
    .withColumn('date_creation', F.to_date('date_creation'))
    .withColumn('telephone', F.when(F.length(F.trim('telephone')) >= 9, F.trim('telephone')))
    .withColumn('email', F.lower(F.trim('email')))
    .drop(*TECH))
assert silver_clients.filter(F.col('wilaya').isNull()).count() == 0, 'wilaya non reconnue'
assert silver_clients.filter(F.col('type_client').isNull()).count() == 0, 'type client non reconnu'
assert silver_clients.count() == silver_clients.select('code_client').distinct().count(), 'doublons clients'
ecrire(silver_clients, 'silver_clients')

silver_produits = (dernier(lire('lh_bronze', 'bronze_produits'), ['code_produit'])
    .withColumn('code_produit', F.upper(F.trim('code_produit')))
    .withColumn('designation', F.trim('designation'))
    .withColumn('cout_achat', F.col('cout_achat').cast('double'))
    .withColumn('prix_vente_ref', F.col('prix_vente_ref').cast('double'))
    .withColumn('actif', F.col('actif') == 'Oui')
    .drop(*TECH))
assert silver_produits.filter('cout_achat <= 0 OR prix_vente_ref < cout_achat').count() == 0, 'produits incohérents'
ecrire(silver_produits, 'silver_produits')

silver_agences = (dernier(lire('lh_bronze', 'bronze_agences'), ['code_agence'])
    .withColumn('code_agence', F.upper(F.trim('code_agence')))
    .drop(*TECH))
ecrire(silver_agences, 'silver_agences')

silver_objectifs = (dernier(lire('lh_bronze', 'bronze_objectifs'), ['mois', 'code_agence'])
    .withColumn('mois', F.to_date(F.concat(F.col('mois'), F.lit('-01'))))
    .withColumn('code_agence', F.upper(F.trim('code_agence')))
    .withColumn('objectif_ca', F.col('objectif_ca').cast('double'))
    .drop(*TECH))
assert silver_objectifs.filter('objectif_ca IS NULL OR objectif_ca <= 0').count() == 0, 'objectifs invalides'
ecrire(silver_objectifs, 'silver_objectifs')

# %% [Cellule 4 : ventes, validation et quarantaine]
bv = lire('lh_bronze', 'bronze_ventes')
total_bronze = bv.count()

v1 = (dernier(bv, ['id_ligne'])
    .withColumn('id_ligne', F.col('id_ligne').cast('int'))
    .withColumn('code_client',  F.upper(F.trim('code_client')))
    .withColumn('code_produit', F.upper(F.trim('code_produit')))
    .withColumn('code_agence',  F.upper(F.trim('code_agence')))
    .withColumn('date_facture', F.coalesce(F.to_date('date_facture', 'dd/MM/yyyy'),
                                           F.to_date('date_facture', 'yyyy-MM-dd')))
    .withColumn('prix_unitaire',
        F.regexp_replace(F.regexp_replace('prix_unitaire', r'[^0-9,.\-]', ''), ',', '.').cast('double'))
    .withColumn('quantite', F.col('quantite').cast('double').cast('int'))
    .withColumn('remise_pct', F.coalesce(F.col('remise_pct').cast('double'), F.lit(0.0)))
    .withColumn('statut', mapping(MAP_STATUT)[norm('statut')]))

cli = silver_clients.select('code_client').withColumn('_ok_client', F.lit(1))
prd = silver_produits.select('code_produit').withColumn('_ok_produit', F.lit(1))
DEBUT, FIN = F.to_date(F.lit('2024-01-01')), F.to_date(F.lit('2025-12-31'))

v2 = (v1.join(cli, 'code_client', 'left').join(prd, 'code_produit', 'left')
    .withColumn('motif_rejet',
        F.when(F.col('date_facture').isNull(), 'date_invalide')
         .when((F.col('date_facture') < DEBUT) | (F.col('date_facture') > FIN), 'hors_periode')
         .when(F.col('quantite').isNull(), 'quantite_manquante')
         .when(F.col('quantite') <= 0, 'quantite_non_positive')
         .when(F.col('quantite') > 1000, 'quantite_aberrante')
         .when(F.col('prix_unitaire').isNull() | (F.col('prix_unitaire') <= 0), 'prix_invalide')
         .when(F.col('statut').isNull(), 'statut_inconnu')
         .when(F.col('_ok_client').isNull(), 'client_inconnu')
         .when(F.col('_ok_produit').isNull(), 'produit_inconnu')))

COLS = ['id_ligne', 'num_facture', 'date_facture', 'code_client', 'code_agence',
        'code_produit', 'quantite', 'prix_unitaire', 'remise_pct', 'statut']
silver_ventes = v2.filter(F.col('motif_rejet').isNull()).select(*COLS)
rejets = v2.filter(F.col('motif_rejet').isNotNull()).select('motif_rejet', *COLS, '_batch_id', '_ingestion_ts')

ecrire(silver_ventes, 'silver_ventes')
ecrire(rejets, 'silver_rejets')

# %% [Cellule 5 : rapport de qualité et seuil d'arrêt]
nb_uniques = v1.count()
nb_rejets = rejets.count()
pct = round(100 * nb_rejets / max(nb_uniques, 1), 2)
print(f'Bronze : {total_bronze} | uniques : {nb_uniques} | silver : {silver_ventes.count()} | rejets : {nb_rejets} ({pct} %)')
rejets.groupBy('motif_rejet').count().orderBy(F.desc('count')).show()

rapport = (rejets.groupBy('motif_rejet').count()
    .withColumn('pct_des_lignes', F.round(100 * F.col('count') / F.lit(nb_uniques), 2))
    .withColumn('controle_ts', F.current_timestamp()))
rapport.write.format('delta').mode('append').saveAsTable('meta_controles_qualite')

# le pipeline s'arrête (et alerte) plutôt que de publier des chiffres douteux
assert pct <= SEUIL_REJETS_PCT, f'Taux de rejets {pct} % supérieur au seuil {SEUIL_REJETS_PCT} %'
