from django.db import migrations
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

def peupler_donnees(apps, schema_editor):
    Categorie = apps.get_model('gestion', 'Categorie')
    Marque = apps.get_model('gestion', 'Marque')
    Magasin = apps.get_model('gestion', 'Magasin')
    Produits = apps.get_model('gestion', 'Produits')
    Fournisseur = apps.get_model('gestion', 'Fournisseur')
    Stock = apps.get_model('gestion', 'Stock')
    MouvementStock = apps.get_model('gestion', 'MouvementStock')

    D = Decimal
    TVA = D('19.25')

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

    FOURNISSEURS = [
        ('Littoral Alimentation SARL', '+237 600 000 001', 'contact@littoral-alim.exemple', 'Zone industrielle de Bassa, Douala', ['Alimentaire']),
        ('Douala Boissons Distribution', '+237 600 000 002', 'contact@douala-boissons.exemple', 'Rue des Brasseries, Douala', ['Boissons']),
        ('Hygiène Plus Cameroun', '+237 600 000 003', 'contact@hygiene-plus.exemple', 'Bonabéri, Douala', ['Hygiène et beauté', 'Entretien maison']),
        ('Mode et Textile Akwa', '+237 600 000 004', 'contact@mode-akwa.exemple', 'Marché de New Bell, Douala', ['Vêtements', 'Chaussures']),
        ('Électro Import Douala', '+237 600 000 005', 'contact@electro-import.exemple', 'Port autonome de Douala', ['Électroménager', 'Électronique']),
    ]

    MAGASINS = [
        ('DLA-01', 'Magasin Principal Akwa', 'Boulevard de la Liberté, Akwa, Douala', True),
        ('DLA-02', 'Magasin Bonapriso', 'Rue Njo-Njo, Bonapriso, Douala', False),
    ]

    PRODUITS = [
        ('ALI001', 'Riz parfumé 25 kg', 'Alimentaire', None, 'sac', 13500, 15500, 80, 20),
        ('ALI002', 'Huile végétale 5 L', 'Alimentaire', None, 'bidon', 7200, 8500, 60, 15),
        ('ALI003', 'Spaghetti 500 g', 'Alimentaire', None, 'paquet', 450, 600, 200, 50),
        ('ALI004', 'Sucre en poudre 1 kg', 'Alimentaire', None, 'paquet', 700, 850, 150, 40),
        ('ALI005', 'Concentré de tomate 400 g', 'Alimentaire', None, 'boîte', 550, 750, 120, 30),
        ('ALI006', 'Cubes Maggi (boîte de 100)', 'Alimentaire', 'Maggi', 'boîte', 2800, 3500, 40, 10),
        ('ALI007', 'Nescafé Classic 200 g', 'Alimentaire', 'Nescafé', 'pot', 3800, 4800, 8, 10),
        ('ALI008', 'Lait en poudre Nido 400 g', 'Alimentaire', 'Nestlé', 'boîte', 3200, 3900, 35, 10),
        ('BOI001', 'Eau minérale Tangui 1,5 L', 'Boissons', 'Tangui', 'bouteille', 250, 350, 300, 80),
        ('BOI002', 'Coca-Cola 1,5 L', 'Boissons', 'Coca-Cola', 'bouteille', 550, 700, 150, 40),
        ('BOI003', 'Fanta Orange 1,5 L', 'Boissons', 'Fanta', 'bouteille', 550, 700, 120, 40),
        ('BOI004', 'Bière 33 Export 65 cl', 'Boissons', '33 Export', 'bouteille', 500, 650, 240, 60),
        ('BOI005', 'Jus d\'orange 1 L', 'Boissons', None, 'brique', 900, 1200, 70, 20),
        ('BOI006', 'Thé Lipton (25 sachets)', 'Boissons', 'Lipton', 'boîte', 900, 1250, 5, 10),
        ('HYG001', 'Dentifrice Colgate 100 ml', 'Hygiène et beauté', 'Colgate', 'tube', 650, 900, 90, 25),
        ('HYG002', 'Savon de toilette', 'Hygiène et beauté', None, 'pièce', 250, 350, 200, 50),
        ('HYG003', 'Lait corporel Nivea 400 ml', 'Hygiène et beauté', 'Nivea', 'flacon', 2800, 3600, 30, 8),
        ('HYG004', 'Papier toilette (pack de 12)', 'Hygiène et beauté', None, 'pack', 2200, 2900, 60, 15),
        ('HYG005', 'Shampoing 400 ml', 'Hygiène et beauté', None, 'flacon', 1800, 2400, 40, 10),
        ('HYG006', 'Couches bébé taille 3 (40)', 'Hygiène et beauté', None, 'paquet', 5500, 7000, 25, 8),
        ('ENT001', 'Lessive en poudre Omo 2 kg', 'Entretien maison', 'Omo', 'sac', 3200, 4000, 50, 15),
        ('ENT002', 'Liquide vaisselle 750 ml', 'Entretien maison', None, 'flacon', 800, 1100, 70, 20),
        ('ENT003', 'Eau de Javel 1 L', 'Entretien maison', None, 'bouteille', 400, 600, 90, 25),
        ('ENT004', 'Éponges (lot de 3)', 'Entretien maison', None, 'lot', 350, 550, 3, 10),
        ('ENT005', 'Insecticide aérosol 400 ml', 'Entretien maison', None, 'flacon', 1800, 2500, 45, 12),
        ('VET001', 'T-shirt homme coton', 'Vêtements', None, 'pièce', 2500, 4500, 60, 15),
        ('VET002', 'Polo homme', 'Vêtements', None, 'pièce', 4000, 7000, 35, 10),
        ('VET003', 'Jean femme', 'Vêtements', None, 'pièce', 7000, 12000, 25, 8),
        ('VET004', 'Robe en pagne', 'Vêtements', None, 'pièce', 6500, 11000, 20, 5),
        ('VET005', 'Chemise homme', 'Vêtements', None, 'pièce', 5000, 8500, 30, 8),
        ('VET006', 'Ensemble de sport enfant', 'Vêtements', None, 'pièce', 4000, 7000, 18, 5),
        ('CHA001', 'Baskets Nike homme', 'Chaussures', 'Nike', 'paire', 18000, 28000, 15, 5),
        ('CHA002', 'Baskets Adidas homme', 'Chaussures', 'Adidas', 'paire', 17000, 26000, 12, 5),
        ('CHA003', 'Sandales femme', 'Chaussures', None, 'paire', 4000, 7500, 30, 8),
        ('CHA004', 'Chaussures de ville homme', 'Chaussures', None, 'paire', 9000, 15000, 14, 5),
        ('CHA005', 'Tongs', 'Chaussures', None, 'paire', 800, 1500, 100, 20),
        ('ELE001', 'Réfrigérateur 2 portes 250 L', 'Électroménager', 'LG', 'pièce', 185000, 235000, 6, 2),
        ('ELE002', 'Ventilateur sur pied', 'Électroménager', 'Binatone', 'pièce', 18000, 25000, 20, 5),
        ('ELE003', 'Mixeur 1,5 L', 'Électroménager', 'Philips', 'pièce', 22000, 32000, 12, 4),
        ('ELE004', 'Fer à repasser', 'Électroménager', 'Tefal', 'pièce', 12000, 18000, 15, 4),
        ('ELE005', 'Bouilloire électrique 1,7 L', 'Électroménager', 'Tefal', 'pièce', 10000, 16000, 18, 5),
        ('ELE006', 'Cuisinière à gaz 4 feux', 'Électroménager', None, 'pièce', 85000, 120000, 4, 2),
        ('ELE007', 'Climatiseur split 1,5 CV', 'Électroménager', 'LG', 'pièce', 190000, 265000, 3, 2),
        ('ELC001', 'Smartphone Samsung Galaxy A15', 'Électronique', 'Samsung', 'pièce', 95000, 125000, 10, 3),
        ('ELC002', 'Téléviseur LED 43 pouces', 'Électronique', 'Hisense', 'pièce', 130000, 175000, 5, 2),
        ('ELC003', 'Écouteurs Bluetooth', 'Électronique', None, 'pièce', 6000, 12000, 40, 10),
        ('ELC004', 'Chargeur rapide USB-C', 'Électronique', 'Samsung', 'pièce', 4500, 8000, 50, 10),
        ('ELC005', 'Powerbank 20000 mAh', 'Électronique', None, 'pièce', 12000, 20000, 25, 8),
    ]

    categories = {}
    for nom, desc in CATEGORIES.items():
        categories[nom], _ = Categorie.objects.get_or_create(nom=nom, defaults={'description': desc})

    marques = {}
    for nom in MARQUES:
        marques[nom], _ = Marque.objects.get_or_create(nom=nom)

    magasins_obj = []
    for code, nom, adresse, en_ligne in MAGASINS:
        m, _ = Magasin.objects.get_or_create(code_magasin=code, defaults={'nom': nom, 'adresse': adresse, 'vente_en_ligne': en_ligne})
        magasins_obj.append(m)
    principal, secondaire = magasins_obj

    produits = {}
    for i, (code, nom, cat, marque, unite, achat, vente, _q, _s) in enumerate(PRODUITS, start=1):
        produits[code], _ = Produits.objects.get_or_create(
            code_produit=code,
            defaults={
                'nom': nom, 'code_barres': f'600{i:010d}',
                'prix_achat': D(achat), 'prix_vente': D(vente),
                'categorie': categories[cat], 'marque': marques[marque] if marque else None,
                'unite_mesure': unite, 'taux_tva': TVA,
            }
        )

    for i, (code, nom, cat, marque, unite, achat, vente, qte_init, seuil) in enumerate(PRODUITS, start=1):
        prod, created = Produits.objects.get_or_create(
            code_produit=code,
            defaults={
                'nom': nom, 'code_barres': f'600{i:010d}',
                'prix_achat': D(achat), 'prix_vente': D(vente),
                'categorie': categories[cat], 'marque': marques[marque] if marque else None,
                'unite_mesure': unite, 'taux_tva': TVA,
            }
        )
        produits[code] = prod
        
        for mag, qte in ((principal, qte_init), (secondaire, qte_init // 2)):
            Stock.objects.get_or_create(
                produit=prod, magasin=mag,
                defaults={'quantite': D(qte), 'seuil_alerte': D(seuil)}
            )


class Migration(migrations.Migration):
    dependencies = [
        ('gestion', '0003_stock_et_mouvements'),  # Remplacez 0001_initial par le nom de votre migration précédente si nécessaire
    ]

    operations = [
        migrations.RunPython(peupler_donnees),
    ]
