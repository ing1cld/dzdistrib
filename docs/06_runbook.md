# Runbook d'exploitation

## Chaque matin (07h00, 5 minutes)
1. Ouvrir **Monitor** : l'exécution de `pl_master_dzdistrib` de 05h00 est-elle réussie ?
2. Ouvrir le rapport `rpt_dzdistrib_sante` : date de dernière actualisation, taux de rejets, écart de réconciliation.
3. Si tout est vert, rien à faire.

## Incident 1 : le pipeline a échoué
1. Monitor, ouvrir l'exécution, repérer l'activité en erreur et son message.
2. Selon l'activité :
   - **Copy data** : la source est indisponible ou le fichier n'est pas arrivé. Vérifier la connexion HTTP, relancer, prévenir le propriétaire de la source.
   - **nb01_bronze** : fichier absent du dossier `Files/landing/.../AAAA/MM/JJ`, ou séparateur modifié. Contrôler le contrat de données.
   - **nb02_silver** : taux de rejets au-dessus du seuil (message du contrôle bloquant). Consulter `silver_rejets`, identifier le motif dominant, demander la correction à la source.
   - **nb03_gold** : table Silver absente ou schéma modifié. Vérifier d'abord que nb02 a réussi.
   - **Actualisation du modèle** : vérifier les droits et la connexion du modèle.
3. Après correction, relancer le pipeline : il est idempotent, aucune suppression manuelle n'est nécessaire.

## Incident 2 : un chiffre est contesté
1. Reproduire le chiffre avec une requête SQL sur `lh_gold`.
2. Comparer avec `lh_silver` puis `lh_bronze` (mêmes filtres) pour trouver la couche où l'écart apparaît.
3. Consulter `silver_rejets` et `meta_controles_qualite` pour la période.
4. Comparer avec la source (fichier dans `Files/landing`).
5. Documenter la cause, corriger, ajouter un contrôle automatique.

## Incident 3 : erreur de traitement à annuler
- Table Delta : `DESCRIBE HISTORY nom_table`, puis `RESTORE TABLE nom_table TO VERSION AS OF n`.
- Notebook ou pipeline : revenir au commit précédent dans Git, puis redéployer.

## Rôles et contacts
| Rôle | Nom | Contact |
|---|---|---|
| Responsable données (astreinte) | À compléter | À compléter |
| Responsable ERP | À compléter | À compléter |
| Responsable CRM | À compléter | À compléter |
| Directeur commercial (validation KPI) | À compléter | À compléter |
