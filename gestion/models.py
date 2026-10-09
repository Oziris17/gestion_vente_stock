from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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
    # Le magasin dont le stock est utilisé pour les commandes faites sur le site.
    vente_en_ligne = models.BooleanField(
        default=False,
        help_text="Cochez pour le magasin dont le stock sert aux commandes du site (un seul possible).")

    class Meta:
        db_table = 'magasin'
        constraints = [
            # Règle appliquée par PostgreSQL lui-même : au plus UN magasin avec vente_en_ligne = vrai.
            models.UniqueConstraint(fields=['vente_en_ligne'], condition=models.Q(vente_en_ligne=True),
                                    name='un_seul_magasin_vente_en_ligne'),
        ]

    def __str__(self):
        return self.nom


class Produits(models.Model):
    id = models.BigAutoField(primary_key=True)
    code_produit = models.CharField(unique=True, max_length=50)
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    code_barres = models.CharField(unique=True, max_length=50, blank=True, null=True)
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    prix_vente = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT)
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, blank=True, null=True)
    unite_mesure = models.CharField(max_length=10)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))])
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
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    date_commande = models.DateTimeField(auto_now_add=True)

    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', 'Brouillon'
        ENVOYEE = 'ENVOYEE', 'Envoyée au fournisseur'
        RECUE_PARTIELLEMENT = 'RECUE_PARTIELLEMENT', 'Reçue partiellement'
        RECUE = 'RECUE', 'Reçue'
        ANNULEE = 'ANNULEE', 'Annulée'

    statut = models.CharField(max_length=30, choices=Statut.choices, default=Statut.BROUILLON)
    remarque = models.TextField(blank=True, null=True)
    cree_par = models.CharField(max_length=100)

    class Meta:
        db_table = 'commande_fournisseur'

    def __str__(self):
        return f"Commande {self.numero_commande} - {self.fournisseur.nom}"


class LigneCommandeFournisseur(models.Model):
    id = models.BigAutoField(primary_key=True)
    commande = models.ForeignKey(CommandeFournisseur, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produits, on_delete=models.PROTECT)
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


# ---------------------------------------------------------------------------
# Commandes passées par les CLIENTS du site (différentes des commandes fournisseur)
# ---------------------------------------------------------------------------
class Commande(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        CONFIRMEE = 'CONFIRMEE', 'Confirmée'
        LIVREE = 'LIVREE', 'Livrée'
        ANNULEE = 'ANNULEE', 'Annulée'

    # settings.AUTH_USER_MODEL = le modèle utilisateur de Django (table auth_user).
    # PROTECT : on ne peut pas supprimer un client qui a des commandes.
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='commandes')
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)

    class Meta:
        db_table = 'commande_client'
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande #{self.pk} - {self.client}"

    @property
    def total(self):
        return sum((ligne.sous_total for ligne in self.lignes.all()), Decimal('0'))


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produits, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # Prix "figé" au moment de l'achat : si le prix du produit change plus tard,
    # les anciennes commandes gardent le prix payé.
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'ligne_commande_client'

    @property
    def sous_total(self):
        return self.prix_unitaire * self.quantite


# ---------------------------------------------------------------------------
# STOCK : quantité actuelle par produit et par magasin + historique des mouvements
# ---------------------------------------------------------------------------
class Stock(models.Model):
    produit = models.ForeignKey(Produits, on_delete=models.PROTECT, related_name='stocks')
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name='stocks')
    quantite = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0'))
    seuil_alerte = models.DecimalField(
        max_digits=12, decimal_places=3, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Une alerte s'affiche quand la quantité est inférieure ou égale à ce seuil.")

    class Meta:
        db_table = 'stock'
        constraints = [
            models.UniqueConstraint(fields=['produit', 'magasin'], name='un_stock_par_produit_et_magasin'),
            # PostgreSQL refuse tout stock négatif, même si le code se trompait.
            models.CheckConstraint(condition=models.Q(quantite__gte=0), name='stock_jamais_negatif'),
        ]
        ordering = ['produit__nom', 'magasin__nom']

    def __str__(self):
        return f"{self.produit} @ {self.magasin} : {self.quantite}"

    @property
    def en_alerte(self):
        return self.quantite <= self.seuil_alerte


class MouvementStock(models.Model):
    """Journal des entrées, sorties et ajustements. On l'écrit, on ne le modifie jamais."""

    class Type(models.TextChoices):
        ENTREE = 'ENTREE', 'Entrée (réception, retour)'
        SORTIE = 'SORTIE', 'Sortie (vente, casse, perte)'
        AJUSTEMENT = 'AJUSTEMENT', 'Ajustement (inventaire)'

    produit = models.ForeignKey(Produits, on_delete=models.PROTECT, related_name='mouvements')
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT, related_name='mouvements')
    type_mouvement = models.CharField(max_length=12, choices=Type.choices)
    # ENTREE/SORTIE : quantité déplacée. AJUSTEMENT : quantité réellement comptée.
    quantite = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0'))])
    quantite_avant = models.DecimalField(max_digits=12, decimal_places=3)
    quantite_apres = models.DecimalField(max_digits=12, decimal_places=3)
    motif = models.CharField(max_length=200, blank=True)
    commande_client = models.ForeignKey(Commande, null=True, blank=True, on_delete=models.SET_NULL,
                                        related_name='mouvements_stock')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                               related_name='mouvements_stock')
    date_mouvement = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mouvement_stock'
        ordering = ['-date_mouvement', '-id']

    def __str__(self):
        return f"{self.get_type_mouvement_display()} {self.quantite} x {self.produit}"
