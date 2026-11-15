# Plan de recette : valeurs de contrôle

Données : `data_formation/` (graine 2026). Tolérance sur les montants : ±2 DA (arrondis ligne à ligne en Gold).

## Volumes par couche
| Contrôle | Attendu |
|---|---|
| bronze_ventes / bronze_clients / bronze_produits / bronze_agences / bronze_objectifs | 12 210 / 308 / 40 / 5 / 120 |
| Identifiants de ligne distincts en Bronze | 12 130 (80 doublons exacts) |
| silver_ventes | 11 965 |
| silver_rejets | 165 : quantite_manquante 60, quantite_non_positive 40, client_inconnu 30, quantite_aberrante 20, hors_periode 15 |
| Rapprochement | 12 210 = 80 + 11 965 + 165 |
| Taux de rejets | 1,36 % (seuil 2 %) |
| silver_clients | 300 (8 doublons supprimés) |
| gold_fact_ventes / gold_dim_date / gold_kpi_agence_mois | 11 965 / 731 / 120 |

## KPI
| KPI | Valeur |
|---|---|
| CA net | 118 856 038,64 |
| Valeur des retours | 3 895 917,61 |
| Taux de retour | 3,17 % |
| Marge brute | 27 951 451,35 |
| Taux de marge | 23,52 % |
| Nombre de factures | 3 932 |
| Panier moyen | 30 227,88 |
| Clients actifs | 300 |
| CA 2024 / 2025 | 61 602 003 / 57 254 036 (croissance −7,06 %) |
| Objectif total / atteinte globale | 127 761 445 / 93,03 % |

## Par agence
| Agence | CA net | Atteinte | Taux de retour |
|---|---|---|---|
| AG01 Béjaïa | 25 676 713 | 89,86 % | 3,38 % |
| AG02 Alger | 34 610 266 | 92,00 % | 3,58 % |
| AG03 Sétif | 21 214 760 | 89,31 % | 2,50 % |
| AG04 Oran | 21 825 242 | 98,29 % | 2,82 % |
| AG05 Constantine | 15 529 059 | 99,49 % | 3,33 % |

## Exploitation et sécurité
- [ ] Le pipeline maître lancé deux fois de suite laisse tous les volumes Silver et Gold inchangés.
- [ ] Une panne simulée (fichier absent) déclenche l'alerte.
- [ ] Un compte de test du rôle Béjaïa voit uniquement l'agence AG01 (CA net 25 676 713).
- [ ] Le déploiement Dev vers Test puis Prod conserve les noms d'éléments et les liens aux Lakehouses.
