from django.contrib import admin
from .models import Categorie, Marque, Magasin, Produits, Fournisseur, CommandeFournisseur, LigneCommandeFournisseur, Livraison, LigneLivraison

@admin.register(Produits)
class ProduitsAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'nom', 'prix_vente', 'categorie', 'actif')
    search_fields = ('nom', 'code_produit', 'code_barres')
    list_filter = ('categorie', 'actif')

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email', 'actif')
    search_fields = ('nom',)

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommandeFournisseur
    extra = 1

@admin.register(CommandeFournisseur)
class CommandeFournisseurAdmin(admin.ModelAdmin):
    list_display = ('numero_commande', 'fournisseur', 'magasin', 'statut', 'date_commande')
    list_filter = ('statut', 'date_commande', 'magasin')
    inlines = [LigneCommandeInline]

class LigneLivraisonInline(admin.TabularInline):
    model = LigneLivraison
    extra = 1

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('numero_livraison', 'commande', 'date_livraison', 'statut')
    list_filter = ('statut', 'date_livraison')
    inlines = [LigneLivraisonInline]

admin.site.register(Categorie)
admin.site.register(Marque)
admin.site.register(Magasin)