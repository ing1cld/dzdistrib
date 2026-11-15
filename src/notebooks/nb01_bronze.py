# nb01_bronze  |  Lakehouse par défaut : lh_bronze
# Rôle : lire les fichiers déposés par le pipeline dans Files/landing et les ajouter, tels quels (texte), dans les tables bronze_*.

# %% [Cellule 1 : paramètres] (menu ... de la cellule : « Basculer la cellule de paramètres »)
DATE_TRAITEMENT = '2026-11-12'      # AAAA-MM-JJ : valeur fournie par le pipeline
BATCH_ID = 'MANUEL_20261112'        # identifiant d'exécution : fourni par le pipeline (@pipeline().RunId)

# %% [Cellule 2 : vérification du Lakehouse par défaut]
ctx = notebookutils.runtime.context
print('Lakehouse par défaut :', ctx.get('defaultLakehouseName'))     # doit afficher lh_bronze

# %% [Cellule 3 : ingestion]
from pyspark.sql import functions as F

JJ = DATE_TRAITEMENT.replace('-', '/')            # 2026/11/12
SOURCES = {
    'ventes':    f'Files/landing/erp/{JJ}/ventes_erp.csv',
    'clients':   f'Files/landing/crm/{JJ}/clients_crm.csv',
    'produits':  f'Files/landing/referentiel/{JJ}/produits.csv',
    'agences':   f'Files/landing/referentiel/{JJ}/agences.csv',
    'objectifs': f'Files/landing/controle_gestion/{JJ}/objectifs.csv',
}

for nom, chemin in SOURCES.items():
    table = 'bronze_' + nom
    df = (spark.read
          .option('header', True)
          .option('sep', ';')
          .option('encoding', 'UTF-8')
          .option('inferSchema', False)          # tout en texte : aucune correction en Bronze
          .csv(chemin))
    df = (df.withColumn('_source_file', F.lit(chemin.split('/')[-1]))
            .withColumn('_batch_id', F.lit(BATCH_ID))
            .withColumn('_ingestion_ts', F.current_timestamp()))

    if spark.catalog.tableExists(table):
        # idempotence : relancer le même lot ne crée pas de doublon
        spark.sql(f"DELETE FROM {table} WHERE _batch_id = '{BATCH_ID}'")

    (df.write.format('delta').mode('append')
       .option('mergeSchema', 'true')
       .saveAsTable(table))
    print(table, ':', df.count(), 'lignes ajoutées | total table :', spark.table(table).count())
