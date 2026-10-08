from django.urls import path
from . import views

urlpatterns = [
    path('', views.tableau_de_bord, name='tableau_de_bord'),
    path('commande/creer/', views.creer_commande, name='creer_commande'),
]