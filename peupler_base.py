"""
peupler_base.py : remplit la base avec des données de test (type hypermarché).

Où le mettre : dans le dossier "mon projet", à côté de manage.py.
Comment le lancer :  python peupler_base.py
Il peut être relancé sans créer de doublons.
Les prix sont en FCFA et sont des ordres de grandeur inventés pour les tests.
"""
import os
from datetime import timedelta
from decimal import Decimal

import django

# 1) Démarrer Django. Nécessaire car on lance ce fichier directement,
#    et non pas avec "manage.py". On lui indique où sont les réglages.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mon_magasin.settings')
django.setup()

# 2) Ces imports doivent venir APRÈS django.setup().
from django.db import transaction
from django.utils import timezone

from gestion.models import (
    Categorie, Marque, Magasin, Produits, Fournisseur,
    CommandeFournisseur, LigneCommandeFournisseur, Livraison, LigneLivraison,
    Stock, MouvementStock,
)

D = Decimal
TVA = D('19.25')  # taux de TVA appliqué à tous les produits de test

# ---------------------------------------------------------------------------
# DONNÉES
# ---------------------------------------------------------------------------
CATEGORIES = {
    'Alimentaire': 'Produits secs et de première nécessité',
    'Boissons': 'Eaux, sodas, bières et jus',
    'Hygiène et beauté': 'Soins du corps, hygiène et bébé',
    'Entretien maison': 'Produits de nettoyage et d\'entretien',
    'Vêtements': 'Vêtements homme, femme et enfant',
    'Chaussures': 'Chaussures et sandales',
    'Électroménager': 'Gros et petit électroménager',
    'Électronique': 'Téléphones, TV et accessoires',
}

MARQUES = [
    'Maggi', 'Nescafé', 'Nestlé', 'Lipton', 'Tangui', 'Coca-Cola', 'Fanta',
    '33 Export', 'Colgate', 'Nivea', 'Omo', 'Nike', 'Adidas', 'LG',
    'Binatone', 'Philips', 'Tefal', 'Samsung', 'Hisense',
]

# (nom, téléphone, email, adresse, catégories fournies)
FOURNISSEURS = [
    ('Littoral Alimentation SARL', '+237 600 000 001', 'contact@littoral-alim.exemple',
     'Zone industrielle de Bassa, Douala', ['Alimentaire']),
    ('Douala Boissons Distribution', '+237 600 000 002', 'contact@douala-boissons.exemple',
     'Rue des Brasseries, Douala', ['Boissons']),
    ('Hygiène Plus Cameroun', '+237 600 000 003', 'contact@hygiene-plus.exemple',
     'Bonabéri, Douala', ['Hygiène et beauté', 'Entretien maison']),
    ('Mode et Textile Akwa', '+237 600 000 004', 'contact@mode-akwa.exemple',
     'Marché de New Bell, Douala', ['Vêtements', 'Chaussures']),
    ('Électro Import Douala', '+237 600 000 005', 'contact@electro-import.exemple',
     'Port autonome de Douala', ['Électroménager', 'Électronique']),
]

# (code, nom, adresse, vente_en_ligne). UN SEUL magasin peut avoir vente_en_ligne = True.
MAGASINS = [
    ('DLA-01', 'Magasin Principal Akwa', 'Boulevard de la Liberté, Akwa, Douala', True),
    ('DLA-02', 'Magasin Bonapriso', 'Rue Njo-Njo, Bonapriso, Douala', False),
]

# (code, nom, catégorie, marque, unité, prix_achat, prix_vente, stock_principal, seuil_alerte)
PRODUITS = [
    # --- Alimentaire
    ('ALI001', 'Riz parfumé 25 kg', 'Alimentaire', None, 'sac', 13500, 15500, 80, 20),
    ('ALI002', 'Huile végétale 5 L', 'Alimentaire', None, 'bidon', 7200, 8500, 60, 15),
    ('ALI003', 'Spaghetti 500 g', 'Alimentaire', None, 'paquet', 450, 600, 200, 50),
    ('ALI004', 'Sucre en poudre 1 kg', 'Alimentaire', None, 'paquet', 700, 850, 150, 40),
    ('ALI005', 'Concentré de tomate 400 g', 'Alimentaire', None, 'boîte', 550, 750, 120, 30),
    ('ALI006', 'Cubes Maggi (boîte de 100)', 'Alimentaire', 'Maggi', 'boîte', 2800, 3500, 40, 10),
    ('ALI007', 'Nescafé Classic 200 g', 'Alimentaire', 'Nescafé', 'pot', 3800, 4800, 8, 10),
    ('ALI008', 'Lait en poudre Nido 400 g', 'Alimentaire', 'Nestlé', 'boîte', 3200, 3900, 35, 10),
    # --- Boissons
    ('BOI001', 'Eau minérale Tangui 1,5 L', 'Boissons', 'Tangui', 'bouteille', 250, 350, 300, 80),
    ('BOI002', 'Coca-Cola 1,5 L', 'Boissons', 'Coca-Cola', 'bouteille', 550, 700, 150, 40),
    ('BOI003', 'Fanta Orange 1,5 L', 'Boissons', 'Fanta', 'bouteille', 550, 700, 120, 40),
    ('BOI004', 'Bière 33 Export 65 cl', 'Boissons', '33 Export', 'bouteille', 500, 650, 240, 60),
    ('BOI005', 'Jus d\'orange 1 L', 'Boissons', None, 'brique', 900, 1200, 70, 20),
    ('BOI006', 'Thé Lipton (25 sachets)', 'Boissons', 'Lipton', 'boîte', 900, 1250, 5, 10),
    # --- Hygiène et beauté
    ('HYG001', 'Dentifrice Colgate 100 ml', 'Hygiène et beauté', 'Colgate', 'tube', 650, 900, 90, 25),
    ('HYG002', 'Savon de toilette', 'Hygiène et beauté', None, 'pièce', 250, 350, 200, 50),
    ('HYG003', 'Lait corporel Nivea 400 ml', 'Hygiène et beauté', 'Nivea', 'flacon', 2800, 3600, 30, 8),
    ('HYG004', 'Papier toilette (pack de 12)', 'Hygiène et beauté', None, 'pack', 2200, 2900, 60, 15),
    ('HYG005', 'Shampoing 400 ml', 'Hygiène et beauté', None, 'flacon', 1800, 2400, 40, 10),
    ('HYG006', 'Couches bébé taille 3 (40)', 'Hygiène et beauté', None, 'paquet', 5500, 7000, 25, 8),
    # --- Entretien maison
    ('ENT001', 'Lessive en poudre Omo 2 kg', 'Entretien maison', 'Omo', 'sac', 3200, 4000, 50, 15),
    ('ENT002', 'Liquide vaisselle 750 ml', 'Entretien maison', None, 'flacon', 800, 1100, 70, 20),
    ('ENT003', 'Eau de Javel 1 L', 'Entretien maison', None, 'bouteille', 400, 600, 90, 25),
    ('ENT004', 'Éponges (lot de 3)', 'Entretien maison', None, 'lot', 350, 550, 3, 10),
    ('ENT005', 'Insecticide aérosol 400 ml', 'Entretien maison', None, 'flacon', 1800, 2500, 45, 12),
    # --- Vêtements
    ('VET001', 'T-shirt homme coton', 'Vêtements', None, 'pièce', 2500, 4500, 60, 15),
    ('VET002', 'Polo homme', 'Vêtements', None, 'pièce', 4000, 7000, 35, 10),
    ('VET003', 'Jean femme', 'Vêtements', None, 'pièce', 7000, 12000, 25, 8),
    ('VET004', 'Robe en pagne', 'Vêtements', None, 'pièce', 6500, 11000, 20, 5),
    ('VET005', 'Chemise homme', 'Vêtements', None, 'pièce', 5000, 8500, 30, 8),
    ('VET006', 'Ensemble de sport enfant', 'Vêtements', None, 'pièce', 4000, 7000, 18, 5),
    # --- Chaussures
    ('CHA001', 'Baskets Nike homme', 'Chaussures', 'Nike', 'paire', 18000, 28000, 15, 5),
    ('CHA002', 'Baskets Adidas homme', 'Chaussures', 'Adidas', 'paire', 17000, 26000, 12, 5),
    ('CHA003', 'Sandales femme', 'Chaussures', None, 'paire', 4000, 7500, 30, 8),
    ('CHA004', 'Chaussures de ville homme', 'Chaussures', None, 'paire', 9000, 15000, 14, 5),
    ('CHA005', 'Tongs', 'Chaussures', None, 'paire', 800, 1500, 100, 20),
    # --- Électroménager
    ('ELE001', 'Réfrigérateur 2 portes 250 L', 'Électroménager', 'LG', 'pièce', 185000, 235000, 6, 2),
    ('ELE002', 'Ventilateur sur pied', 'Électroménager', 'Binatone', 'pièce', 18000, 25000, 20, 5),
    ('ELE003', 'Mixeur 1,5 L', 'Électroménager', 'Philips', 'pièce', 22000, 32000, 12, 4),
    ('ELE004', 'Fer à repasser', 'Électroménager', 'Tefal', 'pièce', 12000, 18000, 15, 4),
    ('ELE005', 'Bouilloire électrique 1,7 L', 'Électroménager', 'Tefal', 'pièce', 10000, 16000, 18, 5),
    ('ELE006', 'Cuisinière à gaz 4 feux', 'Électroménager', None, 'pièce', 85000, 120000, 4, 2),
    ('ELE007', 'Climatiseur split 1,5 CV', 'Électroménager', 'LG', 'pièce', 190000, 265000, 3, 2),
    # --- Électronique
    ('ELC001', 'Smartphone Samsung Galaxy A15', 'Électronique', 'Samsung', 'pièce', 95000, 125000, 10, 3),
    ('ELC002', 'Téléviseur LED 43 pouces', 'Électronique', 'Hisense', 'pièce', 130000, 175000, 5, 2),
    ('ELC003', 'Écouteurs Bluetooth', 'Électronique', None, 'pièce', 6000, 12000, 40, 10),
    ('ELC004', 'Chargeur rapide USB-C', 'Électronique', 'Samsung', 'pièce', 4500, 8000, 50, 10),
    ('ELC005', 'Powerbank 20000 mAh', 'Électronique', None, 'pièce', 12000, 20000, 25, 8),
]

# Mouvements de démonstration sur le magasin principal : (code produit, type, quantité, motif)
# Pour AJUSTEMENT, la quantité est la quantité réellement comptée.
MOUVEMENTS_DEMO = [
    ('ALI001', 'SORTIE', 12, 'Vente en caisse'),
    ('BOI001', 'SORTIE', 45, 'Vente en caisse'),
    ('ALI007', 'SORTIE', 4, 'Vente en caisse'),
    ('ENT004', 'SORTIE', 1, 'Casse en rayon'),
    ('CHA001', 'SORTIE', 2, 'Vente en caisse'),
    ('VET001', 'SORTIE', 3, 'Articles défectueux'),
    ('ELC001', 'ENTREE', 5, 'Réception fournisseur'),
    ('HYG003', 'AJUSTEMENT', 28, 'Inventaire : 2 flacons manquants'),
]


# ---------------------------------------------------------------------------
# FONCTION QUI ENREGISTRE UN MOUVEMENT ET MET LE STOCK À JOUR
# ---------------------------------------------------------------------------
def enregistrer_mouvement(produit, magasin, type_mvt, quantite, motif):
    """Modifie la quantité en stock ET écrit la ligne correspondante dans le journal."""
    stock = Stock.objects.get(produit=produit, magasin=magasin)
    avant = stock.quantite
    quantite = D(quantite)

    if type_mvt == MouvementStock.Type.ENTREE:
        apres = avant + quantite
    elif type_mvt == MouvementStock.Type.SORTIE:
        apres = avant - quantite
        if apres < 0:
            raise ValueError(f'Stock insuffisant pour {produit.nom} ({avant} en stock).')
    else:  # AJUSTEMENT : la quantité donnée est la quantité comptée
        apres = quantite

    stock.quantite = apres
    stock.save()
    MouvementStock.objects.create(
        produit=produit, magasin=magasin, type_mouvement=type_mvt,
        quantite=quantite, quantite_avant=avant, quantite_apres=apres, motif=motif,
    )


# ---------------------------------------------------------------------------
# PROGRAMME PRINCIPAL
# transaction.atomic : tout ou rien. Si une erreur survient, RIEN n'est enregistré.
# ---------------------------------------------------------------------------
@transaction.atomic
def peupler():
    # 1) Catégories. get_or_create : retrouve l'élément s'il existe, sinon le crée.
    categories = {}
    for nom, description in CATEGORIES.items():
        categories[nom], _ = Categorie.objects.get_or_create(
            nom=nom, defaults={'description': description})

    # 2) Marques
    marques = {}
    for nom in MARQUES:
        marques[nom], _ = Marque.objects.get_or_create(nom=nom)

    # 3) Magasins
    magasins = []
    for code, nom, adresse, en_ligne in MAGASINS:
        magasin, _ = Magasin.objects.get_or_create(
            code_magasin=code,
            defaults={'nom': nom, 'adresse': adresse, 'vente_en_ligne': en_ligne})
        magasins.append(magasin)
    principal, secondaire = magasins

    # 4) Fournisseurs, et quel fournisseur fournit quelle catégorie
    fournisseur_de = {}
    fournisseurs = {}
    for nom, tel, email, adresse, cats in FOURNISSEURS:
        f, _ = Fournisseur.objects.get_or_create(
            nom=nom, defaults={'telephone': tel, 'email': email, 'adresse': adresse})
        fournisseurs[nom] = f
        for c in cats:
            fournisseur_de[c] = f

    # 5) Produits (le code-barres fictif est fabriqué à partir du numéro d'ordre)
    produits = {}
    for i, (code, nom, cat, marque, unite, achat, vente, _q, _s) in enumerate(PRODUITS, start=1):
        produits[code], _ = Produits.objects.get_or_create(
            code_produit=code,
            defaults={
                'nom': nom,
                'code_barres': f'600{i:010d}',
                'prix_achat': D(achat),
                'prix_vente': D(vente),
                'categorie': categories[cat],
                'marque': marques[marque] if marque else None,
                'unite_mesure': unite,
                'taux_tva': TVA,
            })

    # 6) Stock et mouvements : seulement si le stock est encore vide (évite les doublons)
    if Stock.objects.exists():
        print('Le stock existe déjà : étape stock et mouvements ignorée.')
    else:
        for code, _n, _c, _m, _u, _a, _v, qte, seuil in PRODUITS:
            produit = produits[code]
            # Magasin principal : quantité complète. Bonapriso : la moitié.
            for magasin, quantite in ((principal, qte), (secondaire, qte // 2)):
                Stock.objects.create(produit=produit, magasin=magasin,
                                     quantite=D(0), seuil_alerte=D(seuil))
                if quantite > 0:
                    enregistrer_mouvement(produit, magasin, MouvementStock.Type.ENTREE,
                                          quantite, 'Stock initial')
        # Quelques mouvements de démonstration (ventes, casse, inventaire...)
        for code, type_mvt, quantite, motif in MOUVEMENTS_DEMO:
            enregistrer_mouvement(produits[code], principal, type_mvt, quantite, motif)

    # 7) Commande fournisseur n°1 : reçue en entier, avec sa livraison
    cmd1, _ = CommandeFournisseur.objects.get_or_create(
        numero_commande='CF-2026-001',
        defaults={'fournisseur': fournisseur_de['Alimentaire'], 'magasin': principal,
                  'statut': CommandeFournisseur.Statut.RECUE, 'cree_par': 'script_de_test'})
    ligne_riz, _ = LigneCommandeFournisseur.objects.get_or_create(
        commande=cmd1, produit=produits['ALI001'],
        defaults={'quantite_commandee': D(40), 'prix_achat_unitaire': D(13500)})
    ligne_spag, _ = LigneCommandeFournisseur.objects.get_or_create(
        commande=cmd1, produit=produits['ALI003'],
        defaults={'quantite_commandee': D(100), 'prix_achat_unitaire': D(450)})

    liv1, _ = Livraison.objects.get_or_create(
        numero_livraison='LIV-2026-001',
        defaults={'commande': cmd1, 'date_livraison': timezone.now() - timedelta(days=5),
                  'statut': 'COMPLETE', 'bon_livraison': 'BL-0001', 'cree_par': 'script_de_test'})
    LigneLivraison.objects.get_or_create(
        livraison=liv1, ligne_commande=ligne_riz,
        defaults={'quantite_recue': D(40), 'quantite_acceptee': D(40),
                  'quantite_endommagee': D(0), 'quantite_manquante': D(0)})
    LigneLivraison.objects.get_or_create(
        livraison=liv1, ligne_commande=ligne_spag,
        defaults={'quantite_recue': D(100), 'quantite_acceptee': D(98),
                  'quantite_endommagee': D(2), 'quantite_manquante': D(0)})

    # 8) Commande fournisseur n°2 : envoyée, pas encore livrée
    cmd2, _ = CommandeFournisseur.objects.get_or_create(
        numero_commande='CF-2026-002',
        defaults={'fournisseur': fournisseur_de['Électroménager'], 'magasin': principal,
                  'statut': CommandeFournisseur.Statut.ENVOYEE, 'cree_par': 'script_de_test'})
    LigneCommandeFournisseur.objects.get_or_create(
        commande=cmd2, produit=produits['ELE002'],
        defaults={'quantite_commandee': D(10), 'prix_achat_unitaire': D(18000)})
    LigneCommandeFournisseur.objects.get_or_create(
        commande=cmd2, produit=produits['ELC004'],
        defaults={'quantite_commandee': D(30), 'prix_achat_unitaire': D(4500)})


if __name__ == '__main__':
    peupler()
    print('Terminé. Contenu de la base :')
    print(f'  Catégories : {Categorie.objects.count()}')
    print(f'  Marques : {Marque.objects.count()}')
    print(f'  Magasins : {Magasin.objects.count()}')
    print(f'  Fournisseurs : {Fournisseur.objects.count()}')
    print(f'  Produits : {Produits.objects.count()}')
    print(f'  Lignes de stock : {Stock.objects.count()}')
    print(f'  Mouvements de stock : {MouvementStock.objects.count()}')
    print(f'  Commandes fournisseur : {CommandeFournisseur.objects.count()}')
