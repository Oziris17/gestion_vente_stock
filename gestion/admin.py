from django.contrib import admin

from .models import (
    Categorie, Commande, CommandeFournisseur, Fournisseur, LigneCommande,
    LigneCommandeFournisseur, LigneLivraison, Livraison, Magasin, Marque, Produits,
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
admin.site.register(Magasin)
