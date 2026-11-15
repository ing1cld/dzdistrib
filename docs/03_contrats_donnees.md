# Contrats de données

Un contrat décrit ce que la source s'engage à livrer. Tout écart déclenche une alerte et une demande de correction à la source.

## Ventes (ERP) : `ventes_erp.csv`
| Colonne | Type attendu | Obligatoire | Règle |
|---|---|---|---|
| id_ligne | entier | oui | Clé unique de la ligne |
| num_facture | texte | oui | Format `F` + 6 chiffres |
| date_facture | date | oui | `AAAA-MM-JJ` (formats historiques `JJ/MM/AAAA` tolérés) ; entre 2024-01-01 et 2025-12-31 |
| code_client | texte | oui | Doit exister dans le CRM |
| code_agence | texte | oui | AG01 à AG05 |
| code_produit | texte | oui | Doit exister dans le référentiel produits |
| quantite | entier | oui | Strictement positif, inférieur ou égal à 1 000 |
| prix_unitaire | décimal | oui | Strictement positif, point décimal, sans unité |
| remise_pct | décimal | non | 0 à 100, vide interprété comme 0 (hypothèse validée par le métier) |
| statut | texte | oui | Livrée, Annulée ou Retour |

Livraison : chaque nuit avant 04h30. En cas de retard, le pipeline de 05h00 échoue et alerte.

## Clients (CRM) : `clients_crm.csv`
code_client (clé unique), nom_client, wilaya (une des 5 wilayas), type_client (Grossiste, Détaillant, Restaurant), date_creation, telephone (facultatif), email (facultatif).

## Produits : `produits.csv`
code_produit (clé unique), designation, categorie, marque, cout_achat (> 0), prix_vente_ref (>= cout_achat), actif (Oui ou Non).

## Agences : `agences.csv`
code_agence (clé unique), nom_agence, wilaya, responsable.

## Objectifs : `objectifs.csv`
mois (`AAAA-MM`), code_agence, objectif_ca (> 0). Un seul objectif par couple mois et agence.
