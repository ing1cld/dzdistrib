"""Génère le jeu de données DzDistrib (ERP + CRM) avec des défauts de qualité volontaires."""
import random
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
random.seed(2026)
OUT = Path('data_formation')
OUT.mkdir(exist_ok=True)

# ---------- 1. AGENCES ----------
agences = pd.DataFrame({
    'code_agence': ['AG01', 'AG02', 'AG03', 'AG04', 'AG05'],
    'nom_agence': ['Agence Béjaïa', 'Agence Alger', 'Agence Sétif', 'Agence Oran', 'Agence Constantine'],
    'wilaya': ['Béjaïa', 'Alger', 'Sétif', 'Oran', 'Constantine'],
    'responsable': ['Karim B.', 'Samia L.', 'Nadir H.', 'Leila M.', 'Yacine T.'],
})

# ---------- 2. PRODUITS ----------
cats = {
    'Boissons': ['Jus orange', 'Limonade', 'Eau minérale', 'Soda cola', 'Boisson gazeuse citron', 'Jus pomme', 'Eau gazeuse', 'Thé glacé', 'Sirop grenadine', 'Boisson énergétique'],
    'Produits laitiers': ['Lait UHT', 'Yaourt nature', 'Fromage fondu', 'Beurre', 'Crème dessert', 'Lait en poudre', 'Camembert', 'Yaourt aux fruits', 'Lben', 'Fromage râpé'],
    'Épicerie': ['Huile de table', 'Sucre', 'Semoule', 'Pâtes spaghetti', 'Farine', 'Café moulu', 'Tomate concentrée', 'Couscous', 'Lentilles', 'Riz'],
    'Hygiène': ['Savon', 'Shampoing', 'Dentifrice', 'Lessive', 'Mouchoirs', 'Gel douche', 'Liquide vaisselle', 'Papier toilette', 'Eau de Javel', 'Déodorant'],
}
rows = []
i = 1
for cat, noms in cats.items():
    for nom in noms:
        cout = round(float(rng.uniform(40, 600)), 2)
        rows.append({'code_produit': f'P{i:03d}', 'designation': nom, 'categorie': cat,
                     'marque': random.choice(['Marque A', 'Marque B', 'Marque C', 'Marque D']),
                     'cout_achat': cout,
                     'prix_vente_ref': round(cout * float(rng.uniform(1.15, 1.6)), 2),
                     'actif': random.choice(['Oui'] * 9 + ['Non'])})
        i += 1
produits = pd.DataFrame(rows)

# ---------- 3. CLIENTS (CRM) ----------
wil_variants = {
    'Béjaïa': ['Béjaïa', 'Bejaia', 'BEJAIA', 'béjaia '],
    'Alger': ['Alger', 'ALGER', 'alger', 'Alger '],
    'Sétif': ['Sétif', 'Setif', 'SETIF'],
    'Oran': ['Oran', 'ORAN', 'oran'],
    'Constantine': ['Constantine', 'constantine', 'CONSTANTINE'],
}
type_variants = {
    'Grossiste': ['Grossiste', 'grossiste ', 'GROSSISTE'],
    'Détaillant': ['Détaillant', 'detaillant', 'Détaillant '],
    'Restaurant': ['Restaurant', 'restaurant'],
}
n_cli = 300
wil_true = rng.choice(list(wil_variants), n_cli, p=[.22, .30, .18, .18, .12])
typ_true = rng.choice(list(type_variants), n_cli, p=[.2, .6, .2])
clients = pd.DataFrame({
    'code_client': [f'C{k:04d}' for k in range(1, n_cli + 1)],
    'nom_client': [f'client {k} sarl' if k % 3 else f'ETS CLIENT {k}' for k in range(1, n_cli + 1)],
    'wilaya': [random.choice(wil_variants[w]) for w in wil_true],
    'type_client': [random.choice(type_variants[t]) for t in typ_true],
    'date_creation': (pd.to_datetime('2019-01-01') + pd.to_timedelta(rng.integers(0, 2200, n_cli), unit='D')).strftime('%Y-%m-%d'),
    'telephone': [f'05{rng.integers(10, 99)}{rng.integers(100000, 999999)}' for _ in range(n_cli)],
    'email': [f'contact{k}@exemple.dz' for k in range(1, n_cli + 1)],
})
clients.loc[rng.choice(n_cli, 30, replace=False), 'telephone'] = None   # téléphones manquants
clients.loc[rng.choice(n_cli, 40, replace=False), 'email'] = None
dup = clients.sample(8, random_state=3).copy()                           # doublons clients
dup['date_creation'] = '2025-06-01'
clients = pd.concat([clients, dup], ignore_index=True)

# ---------- 4. VENTES (ERP) ----------
n_fact = 4000
ids_clients = [f'C{k:04d}' for k in range(1, n_cli + 1)]
fact = pd.DataFrame({
    'num_facture': [f'F{100000 + k}' for k in range(n_fact)],
    'date_facture': pd.to_datetime('2024-01-01') + pd.to_timedelta(rng.integers(0, 731, n_fact), unit='D'),
    'code_client': rng.choice(ids_clients, n_fact),
    'code_agence': rng.choice(agences['code_agence'], n_fact, p=[.22, .30, .18, .18, .12]),
    'nb_lignes': rng.integers(1, 6, n_fact),
})
v = fact.loc[fact.index.repeat(fact['nb_lignes'])].drop(columns='nb_lignes').reset_index(drop=True)
v.insert(0, 'id_ligne', range(1, len(v) + 1))
v['code_produit'] = rng.choice(produits['code_produit'], len(v))
ref = produits.set_index('code_produit')['prix_vente_ref']
v['quantite'] = rng.integers(1, 51, len(v)).astype(float)
v['prix_unitaire'] = (v['code_produit'].map(ref) * rng.uniform(0.95, 1.05, len(v))).round(2)
v['remise_pct'] = rng.choice([0, 0, 0, 5, 10, 15], len(v)).astype(float)
v['statut'] = rng.choice(['Livrée', 'Annulée', 'Retour'], len(v), p=[.92, .05, .03])

# --- défauts volontaires ---
n = len(v)
idx = rng.permutation(n)
v.loc[idx[:60], 'quantite'] = np.nan                    # quantités manquantes
v.loc[idx[60:100], 'quantite'] = -v.loc[idx[60:100], 'quantite']   # quantités négatives
v.loc[idx[100:120], 'quantite'] = 9999                  # aberrantes
v.loc[idx[120:150], 'code_client'] = 'C9999'            # client inconnu
v.loc[idx[150:200], 'code_produit'] = v.loc[idx[150:200], 'code_produit'].str.lower()  # casse
v.loc[idx[200:230], 'remise_pct'] = np.nan              # remise manquante
v.loc[idx[230:260], 'statut'] = v.loc[idx[230:260], 'statut'].str.upper().str.replace('É', 'E')  # LIVREE...
v.loc[idx[260:275], 'date_facture'] = pd.to_datetime('2027-03-15')  # dates hors période

def fmt_date(d):
    return d.strftime('%d/%m/%Y') if random.random() < 0.3 else d.strftime('%Y-%m-%d')

def fmt_prix(p):
    if random.random() < 0.10:
        return f'{p:,.2f}'.replace(',', ' ').replace('.', ',') + ' DA'
    return str(p)

v['date_facture'] = v['date_facture'].apply(fmt_date)
v['prix_unitaire'] = v['prix_unitaire'].apply(fmt_prix)
v['quantite'] = v['quantite'].apply(lambda q: q if pd.isna(q) else int(q))
v = pd.concat([v, v.sample(80, random_state=7)], ignore_index=True)   # doublons exacts
v = v.sample(frac=1, random_state=11).reset_index(drop=True)

# ---------- 5. OBJECTIFS ----------
base = {'AG01': 1.1e6, 'AG02': 1.5e6, 'AG03': 0.9e6, 'AG04': 0.9e6, 'AG05': 0.6e6}
mois = pd.period_range('2024-01', '2025-12', freq='M').astype(str)
objectifs = pd.DataFrame([{'mois': m, 'code_agence': a, 'objectif_ca': round(b * float(rng.uniform(0.9, 1.2)), 0)}
                          for m in mois for a, b in base.items()])

# ---------- Export ----------
agences.to_csv(OUT / 'agences.csv', sep=';', index=False, encoding='utf-8')
produits.to_csv(OUT / 'produits.csv', sep=';', index=False, encoding='utf-8')
clients.to_csv(OUT / 'clients_crm.csv', sep=';', index=False, encoding='utf-8')
v.to_csv(OUT / 'ventes_erp.csv', sep=';', index=False, encoding='utf-8')
objectifs.to_csv(OUT / 'objectifs.csv', sep=';', index=False, encoding='utf-8')
for f in sorted(OUT.glob('*.csv')):
    print(f.name, len(pd.read_csv(f, sep=';')))
