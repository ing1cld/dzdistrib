# Matrice des sources

| Source | Système | Type | Format | Fréquence | Volume (période) | Propriétaire | Méthode d'ingestion | Contraintes |
|---|---|---|---|---|---|---|---|---|
| Ventes | ERP | Export de fichier | CSV, séparateur `;`, UTF-8 | Quotidienne | environ 12 000 lignes | DSI / ERP | **Copy data** (pipeline) depuis HTTP vers `Files/landing/erp` | Dates en deux formats, prix avec unité, doublons possibles |
| Clients | CRM | Export de fichier | CSV, `;` | Quotidienne | environ 300 lignes | Équipe CRM | **Copy data** vers `Files/landing/crm` | Orthographes multiples, doublons, téléphones manquants |
| Produits | Référentiel | Fichier | CSV, `;` | À la demande | 40 lignes | Achats | **Copy data** vers `Files/landing/referentiel` | Aucune |
| Agences | Référentiel | Fichier | CSV, `;` | À la demande | 5 lignes | Direction | **Copy data** vers `Files/landing/referentiel` | Aucune |
| Objectifs | Contrôle de gestion | Fichier | CSV, `;` (ou Excel) | Mensuelle | 120 lignes | Contrôle de gestion | **Copy data** (ou **Dataflow Gen2** pour la version Excel) | Un objectif par mois et par agence |

Les données sources de ce dépôt sont fictives et servent à simuler ces livraisons.
