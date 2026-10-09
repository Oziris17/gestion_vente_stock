from django.urls import path

from . import views

urlpatterns = [
    # --- Public / clients ---
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription_client, name='inscription'),
    path('commander/<int:produit_id>/', views.passer_commande, name='passer_commande'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),

    # --- Espace gestion (staff) ---
    path('gestion/connexion/', views.StaffLoginView.as_view(), name='gestion_login'),
    path('gestion/', views.TableauDeBord.as_view(), name='tableau_de_bord'),
    path('gestion/produits/', views.ProduitListe.as_view(), name='produit_liste'),
    path('gestion/produits/nouveau/', views.ProduitCreer.as_view(), name='produit_creer'),
    path('gestion/produits/<int:pk>/modifier/', views.ProduitModifier.as_view(), name='produit_modifier'),
    path('gestion/commande/creer/', views.CommandeFournisseurCreer.as_view(), name='creer_commande'),
    path('gestion/stock/', views.StockListe.as_view(), name='stock_liste'),
    path('gestion/stock/<int:pk>/seuil/', views.StockSeuil.as_view(), name='stock_seuil'),
    path('gestion/stock/mouvement/nouveau/', views.MouvementCreer.as_view(), name='mouvement_creer'),
    path('gestion/stock/mouvements/', views.MouvementListe.as_view(), name='mouvement_liste'),
    path('gestion/commandes-clients/', views.CommandeClientListe.as_view(), name='commande_client_liste'),
    path('gestion/commandes-clients/<int:pk>/statut/', views.CommandeClientStatut.as_view(), name='commande_client_statut'),
]
