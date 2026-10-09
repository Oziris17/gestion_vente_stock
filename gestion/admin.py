from django.contrib import admin

from .models import (
    Categorie, Commande, CommandeFournisseur, Fournisseur, LigneCommande,
    LigneCommandeFournisseur, LigneLivraison, Livraison, Magasin, Marque, MouvementStock, Produits, Stock,
)


@admin.register(Produits)
class ProduitsAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'nom', 'prix_vente', 'categorie', 'actif')
    search_fields = ('nom', 'code_produit', 'code_barres')
    list_filter = ('categorie', 'actif')


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email', 'actif')
    search_fields = ('nom',)


class LigneCommandeFournisseurInline(admin.TabularInline):
    model = LigneCommandeFournisseur
    extra = 1


@admin.register(CommandeFournisseur)
class CommandeFournisseurAdmin(admin.ModelAdmin):
    list_display = ('numero_commande', 'fournisseur', 'magasin', 'statut', 'date_commande')
    list_filter = ('statut', 'date_commande', 'magasin')
    inlines = [LigneCommandeFournisseurInline]


class LigneLivraisonInline(admin.TabularInline):
    model = LigneLivraison
    extra = 1


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('numero_livraison', 'commande', 'date_livraison', 'statut')
    list_filter = ('statut', 'date_livraison')
    inlines = [LigneLivraisonInline]


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'statut', 'date_commande')
    list_filter = ('statut', 'date_commande')
    inlines = [LigneCommandeInline]


admin.site.register(Categorie)
admin.site.register(Marque)


@admin.register(Magasin)
class MagasinAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_magasin', 'actif', 'vente_en_ligne')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """La quantité n'est pas modifiable ici : elle ne change que par un mouvement de stock."""
    list_display = ('produit', 'magasin', 'quantite', 'seuil_alerte')
    list_filter = ('magasin',)
    search_fields = ('produit__nom', 'produit__code_produit')
    readonly_fields = ('produit', 'magasin', 'quantite')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    """Journal en lecture seule : on n'ajoute, ne modifie ni ne supprime un mouvement ici."""
    list_display = ('date_mouvement', 'produit', 'magasin', 'type_mouvement', 'quantite', 'quantite_avant', 'quantite_apres', 'auteur')
    list_filter = ('type_mouvement', 'magasin')
    search_fields = ('produit__nom', 'motif')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
