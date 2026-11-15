# Fiches KPI (à faire valider par le Directeur commercial)

**Règles de gestion communes**
- Montant d'une ligne = quantité × prix unitaire × (1 − remise_pct / 100).
- Les lignes au statut Annulée sont exclues de tous les calculs.
- Le CA net ne compte que les lignes Livrée. Les retours (statut Retour) sont comptés à part.
- Coût d'une ligne = quantité × cout_achat du produit.
- Période d'analyse : 01/01/2024 au 31/12/2025. Les lignes hors période sont rejetées.

| KPI | Définition métier | Formule | Granularité | Source | Fraîcheur |
|---|---|---|---|---|---|
| CA net | Ventes livrées après remise | Somme du montant des lignes Livrée | mois, agence, produit, client | ERP (ventes) | J-1, 07h00 |
| Marge brute | CA net moins coût d'achat | CA net − somme des coûts des lignes Livrée | idem | ERP + référentiel produits | J-1, 07h00 |
| Taux de marge | Part de marge dans le CA | Marge brute / CA net | idem | idem | J-1, 07h00 |
| Valeur des retours | Marchandise retournée | Somme du montant des lignes Retour | mois, agence, produit | ERP | J-1, 07h00 |
| Taux de retour | Poids des retours | Retours / (CA net + Retours) | agence, produit | ERP | J-1, 07h00 |
| Nombre de factures | Factures distinctes livrées | Nombre de num_facture distincts (Livrée) | mois, agence | ERP | J-1, 07h00 |
| Panier moyen | Valeur moyenne d'une facture | CA net / nombre de factures | mois, agence, type de client | ERP | J-1, 07h00 |
| Clients actifs | Clients ayant acheté | Nombre de code_client distincts (Livrée) | mois, agence | ERP + CRM | J-1, 07h00 |
| Taux d'atteinte | Réalisé par rapport à l'objectif | CA net / objectif_ca | mois, agence | ERP + Contrôle de gestion | J-1, 07h00 |
| Croissance annuelle | Variation du CA d'une année à l'autre | (CA N − CA N-1) / CA N-1 | global, agence | ERP | J-1, 07h00 |

**Propriétaire de la définition** : Directeur commercial. Toute modification passe par une demande de changement documentée.
