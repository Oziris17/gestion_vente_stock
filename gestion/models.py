from django.db import models

class Categorie(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categorie'

    def __str__(self):
        return self.nom


class Marque(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'marque'

    def __str__(self):
        return self.nom


class Magasin(models.Model):
    id = models.BigAutoField(primary_key=True)
    code_magasin = models.CharField(unique=True, max_length=30)
    nom = models.CharField(unique=True, max_length=150)
    adresse = models.TextField(blank=True, null=True)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = 'magasin'

    def __str__(self):
        return self.nom


class Produits(models.Model):
    id = models.BigAutoField(primary_key=True)
    code_produit = models.CharField(unique=True, max_length=50)
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    code_barres = models.CharField(unique=True, max_length=50, blank=True, null=True)
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=12, decimal_places=2)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, blank=True, null=True)
    unite_mesure = models.CharField(max_length=10)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = 'produits'

    def __str__(self):
        return self.nom


class Fournisseur(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(unique=True, max_length=150)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = 'fournisseur'

    def __str__(self):
        return self.nom


class CommandeFournisseur(models.Model):
    id = models.BigAutoField(primary_key=True)
    numero_commande = models.CharField(unique=True, max_length=50)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=30)
    remarque = models.TextField(blank=True, null=True)
    cree_par = models.CharField(max_length=100)

    class Meta:
        db_table = 'commande_fournisseur'

    def __str__(self):
        return f"Commande {self.numero_commande} - {self.fournisseur.nom}"


class LigneCommandeFournisseur(models.Model):
    id = models.BigAutoField(primary_key=True)
    commande = models.ForeignKey(CommandeFournisseur, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produits, on_delete=models.CASCADE)
    quantite_commandee = models.DecimalField(max_digits=12, decimal_places=3)
    prix_achat_unitaire = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'ligne_commande_fournisseur'
        unique_together = (('commande', 'produit'),)


class Livraison(models.Model):
    id = models.BigAutoField(primary_key=True)
    numero_livraison = models.CharField(unique=True, max_length=50)
    commande = models.ForeignKey(CommandeFournisseur, on_delete=models.CASCADE)
    date_livraison = models.DateTimeField()
    statut = models.CharField(max_length=30)
    bon_livraison = models.CharField(max_length=100, blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)
    cree_par = models.CharField(max_length=100)

    class Meta:
        db_table = 'livraison'

    def __str__(self):
        return f"Livraison {self.numero_livraison}"


class LigneLivraison(models.Model):
    id = models.BigAutoField(primary_key=True)
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE)
    ligne_commande = models.ForeignKey(LigneCommandeFournisseur, on_delete=models.CASCADE)
    quantite_recue = models.DecimalField(max_digits=12, decimal_places=3)
    quantite_acceptee = models.DecimalField(max_digits=12, decimal_places=3)
    quantite_endommagee = models.DecimalField(max_digits=12, decimal_places=3)
    quantite_manquante = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        db_table = 'ligne_livraison'
        unique_together = (('livraison', 'ligne_commande'),)