from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from gestion.forms import ClientAuthenticationForm

urlpatterns = [
    # Le site d'administration Django : réservé à l'admin principal (superutilisateur)
    path('admin/', admin.site.urls),

    # Connexion / déconnexion des CLIENTS
    path('connexion/', auth_views.LoginView.as_view(
        template_name='gestion/login.html',
        authentication_form=ClientAuthenticationForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),

    # Toutes les autres pages sont dans l'application "gestion"
    path('', include('gestion.urls')),
]
