-- À exécuter sur le point de terminaison SQL de lh_gold (nouvelle requête SQL)

-- 1. Volumes
SELECT 'gold_fact_ventes' AS table_nom, COUNT(*) AS nb FROM gold_fact_ventes
UNION ALL SELECT 'gold_dim_date', COUNT(*) FROM gold_dim_date
UNION ALL SELECT 'gold_dim_client', COUNT(*) FROM gold_dim_client
UNION ALL SELECT 'gold_dim_produit', COUNT(*) FROM gold_dim_produit
UNION ALL SELECT 'gold_kpi_agence_mois', COUNT(*) FROM gold_kpi_agence_mois;
-- attendu : 11965, 731, 300, 40, 120

-- 2. KPI globaux (Livrée)
SELECT ROUND(SUM(montant_net), 2) AS ca_net,
       ROUND(SUM(marge), 2) AS marge_brute,
       COUNT(DISTINCT num_facture) AS nb_factures,
       COUNT(DISTINCT code_client) AS clients_actifs
FROM gold_fact_ventes
WHERE statut = 'Livrée';
-- attendu : 118856038,64 | 27951451,35 | 3932 | 300 (écart toléré de 2 sur les montants)

-- 3. Retours
SELECT ROUND(SUM(montant_net), 2) AS valeur_retours
FROM gold_fact_ventes
WHERE statut = 'Retour';
-- attendu : 3895917,61

-- 4. CA net par année
SELECT YEAR(date_facture) AS annee, ROUND(SUM(montant_net), 0) AS ca_net
FROM gold_fact_ventes
WHERE statut = 'Livrée'
GROUP BY YEAR(date_facture)
ORDER BY annee;
-- attendu : 2024 = 61602003 ; 2025 = 57254036

-- 5. Intégrité des clés (doit renvoyer 0, 0, 0)
SELECT
  (SELECT COUNT(*) FROM gold_fact_ventes f LEFT JOIN gold_dim_client  d ON d.code_client  = f.code_client  WHERE d.code_client  IS NULL) AS sans_client,
  (SELECT COUNT(*) FROM gold_fact_ventes f LEFT JOIN gold_dim_produit d ON d.code_produit = f.code_produit WHERE d.code_produit IS NULL) AS sans_produit,
  (SELECT COUNT(*) FROM gold_fact_ventes f LEFT JOIN gold_dim_agence  d ON d.code_agence  = f.code_agence  WHERE d.code_agence  IS NULL) AS sans_agence;

-- 6. Atteinte globale des objectifs
SELECT ROUND(SUM(ca_net) / SUM(objectif_ca), 4) AS taux_atteinte_global
FROM gold_kpi_agence_mois;
-- attendu : 0,9303

-- 7. Rejets par motif
SELECT motif_rejet, nb_lignes FROM gold_qualite_rejets ORDER BY nb_lignes DESC;
-- attendu : quantite_manquante 60, quantite_non_positive 40, client_inconnu 30, quantite_aberrante 20, hors_periode 15
