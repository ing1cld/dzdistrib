# nb03_gold  |  Lakehouse par défaut : lh_gold
# Rôle : lire lh_silver et construire le modèle en étoile dans lh_gold.

# %% [Cellule 1 : lecture inter-Lakehouse]
ctx = notebookutils.runtime.context
WS = ctx.get('currentWorkspaceId')
print('Espace de travail :', WS, '| Lakehouse par défaut :', ctx.get('defaultLakehouseName'))   # lh_gold

def lire(lakehouse, table):
    chemin = f'abfss://{WS}@onelake.dfs.fabric.microsoft.com/{lakehouse}.Lakehouse/Tables/{table}'
    return spark.read.format('delta').load(chemin)

# %% [Cellule 2 : dimensions et faits]
from pyspark.sql import functions as F

def ecrire(df, nom):
    (df.write.format('delta').mode('overwrite').option('overwriteSchema', 'true').saveAsTable(nom))
    print(nom, ':', spark.table(nom).count(), 'lignes')

sv = lire('lh_silver', 'silver_ventes')
sp = lire('lh_silver', 'silver_produits')
sc = lire('lh_silver', 'silver_clients')
sa = lire('lh_silver', 'silver_agences')
so = lire('lh_silver', 'silver_objectifs')

ecrire(sp.select('code_produit', 'designation', 'categorie', 'marque', 'cout_achat', 'prix_vente_ref', 'actif'), 'gold_dim_produit')
ecrire(sc.select('code_client', 'nom_client', 'wilaya', 'type_client', 'date_creation'), 'gold_dim_client')   # pas de téléphone ni d'email en Gold
ecrire(sa, 'gold_dim_agence')

MOIS_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet',
           'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
dim_date = (spark.sql("SELECT explode(sequence(to_date('2024-01-01'), to_date('2025-12-31'), interval 1 day)) AS date")
    .withColumn('annee', F.year('date'))
    .withColumn('trimestre', F.quarter('date'))
    .withColumn('mois_num', F.month('date'))
    .withColumn('mois_nom', F.element_at(F.array(*[F.lit(m) for m in MOIS_FR]), F.month('date')))
    .withColumn('annee_mois', F.date_format('date', 'yyyy-MM'))
    .withColumn('jour_semaine', F.expr('weekday(date) + 1')))
ecrire(dim_date, 'gold_dim_date')

fact = (sv.join(sp.select('code_produit', 'cout_achat'), 'code_produit', 'inner')
    .withColumn('prix_net_unitaire', F.col('prix_unitaire') * (1 - F.col('remise_pct') / 100))
    .withColumn('montant_net', F.round(F.col('quantite') * F.col('prix_net_unitaire'), 2))
    .withColumn('cout_total', F.round(F.col('quantite') * F.col('cout_achat'), 2))
    .withColumn('marge', F.round(F.col('montant_net') - F.col('cout_total'), 2))
    .select('id_ligne', 'num_facture', 'date_facture', 'code_client', 'code_produit',
            'code_agence', 'statut', 'quantite', 'prix_unitaire', 'remise_pct',
            'montant_net', 'cout_total', 'marge'))
ecrire(fact, 'gold_fact_ventes')

# %% [Cellule 3 : objectifs, qualité et KPI précalculés]
ecrire(so, 'gold_objectifs')
ecrire(lire('lh_silver', 'silver_rejets').groupBy('motif_rejet').agg(F.count('*').alias('nb_lignes')), 'gold_qualite_rejets')

kpi = (fact.filter(F.col('statut') == 'Livrée')
    .groupBy(F.trunc('date_facture', 'month').alias('mois'), 'code_agence')
    .agg(F.sum('montant_net').alias('ca_net'),
         F.sum('marge').alias('marge'),
         F.countDistinct('num_facture').alias('nb_factures'),
         F.countDistinct('code_client').alias('nb_clients_actifs'))
    .join(so, ['mois', 'code_agence'], 'left')
    .withColumn('panier_moyen', F.round(F.col('ca_net') / F.col('nb_factures'), 2))
    .withColumn('taux_marge', F.round(F.col('marge') / F.col('ca_net'), 4))
    .withColumn('taux_atteinte', F.round(F.col('ca_net') / F.col('objectif_ca'), 4)))
ecrire(kpi, 'gold_kpi_agence_mois')
