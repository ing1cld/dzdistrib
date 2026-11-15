# DzDistrib — données de formation

Script de génération de données synthétiques ERP/CRM, avec des défauts de qualité volontaires pour les exercices de nettoyage et d'analyse.

## Générer les fichiers CSV

```bash
python -m pip install -r requirements.txt
python generer_donnees.py
```

Les cinq fichiers sont créés dans `data_formation/` : `agences.csv`, `produits.csv`, `clients_crm.csv`, `ventes_erp.csv` et `objectifs.csv`. La génération est déterministe grâce à la graine `2026`.
