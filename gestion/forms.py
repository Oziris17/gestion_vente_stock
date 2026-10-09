from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Commande, CommandeFournisseur, Magasin, MouvementStock, Produits, Stock

User = get_user_model()


class BootstrapMixin:
    """Ajoute automatiquement les classes CSS Bootstrap à tous les champs d'un formulaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css = 'form-select'
            else:
                css = 'form-control'
            field.widget.attrs['class'] = css


# --- Comptes --------------------------------------------------------------
class InscriptionClientForm(BootstrapMixin, UserCreationForm):
    """Inscription d'un CLIENT. Ne crée jamais un compte staff."""

    email = forms.EmailField(label='Adresse e-mail')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Un compte existe déjà avec cette adresse e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Verrou de sécurité : un client n'est JAMAIS staff ni superutilisateur,
        # quoi qu'il arrive dans la requête envoyée par le navigateur.
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class ClientAuthenticationForm(BootstrapMixin, AuthenticationForm):
    """Formulaire de connexion des clients (même logique que Django, avec le style Bootstrap)."""


class StaffAuthenticationForm(BootstrapMixin, AuthenticationForm):
    """Connexion de l'espace gestion : refuse tout compte qui n'est pas staff."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)  # refuse d'abord les comptes désactivés
        if not user.is_staff:
            # Message volontairement vague : on ne révèle pas que le mot de passe était bon.
            raise forms.ValidationError(
                "Identifiants incorrects ou compte non autorisé pour l'espace gestion.",
                code='non_staff',
            )


# --- Clients : passer commande -------------------------------------------
class LigneCommandeForm(BootstrapMixin, forms.Form):
    quantite = forms.IntegerField(label='Quantité', min_value=1, max_value=999, initial=1)


# --- Gestion --------------------------------------------------------------
class ProduitForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Produits
        fields = ['code_produit', 'nom', 'description', 'code_barres', 'prix_achat', 'prix_vente',
                  'categorie', 'marque', 'unite_mesure', 'taux_tva', 'actif']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class CommandeFournisseurForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = CommandeFournisseur
        fields = ['numero_commande', 'fournisseur', 'magasin', 'statut', 'remarque']
        widgets = {'remarque': forms.Textarea(attrs={'rows': 3})}


class StatutCommandeForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['statut']

    def clean_statut(self):
        nouveau = self.cleaned_data['statut']
        # Une commande annulée a déjà rendu son stock : on ne la réactive pas
        # (il faudrait re-vérifier le stock). Il faut en créer une nouvelle.
        if self.initial.get('statut') == Commande.Statut.ANNULEE and nouveau != Commande.Statut.ANNULEE:
            raise forms.ValidationError("Une commande annulée ne peut pas être réactivée.")
        return nouveau


class MouvementStockForm(BootstrapMixin, forms.Form):
    produit = forms.ModelChoiceField(queryset=Produits.objects.filter(actif=True).order_by('nom'))
    magasin = forms.ModelChoiceField(queryset=Magasin.objects.filter(actif=True).order_by('nom'))
    type_mouvement = forms.ChoiceField(label='Type de mouvement', choices=MouvementStock.Type.choices)
    quantite = forms.DecimalField(
        label='Quantité', max_digits=12, decimal_places=3, min_value=0,
        help_text="Pour un ajustement (inventaire), saisissez la quantité réellement comptée.")
    motif = forms.CharField(label='Motif (facultatif)', max_length=200, required=False)

    def clean(self):
        data = super().clean()
        type_m, quantite = data.get('type_mouvement'), data.get('quantite')
        if quantite is not None and type_m in (MouvementStock.Type.ENTREE, MouvementStock.Type.SORTIE) and quantite <= 0:
            self.add_error('quantite', "La quantité doit être supérieure à 0.")
        return data


class SeuilStockForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['seuil_alerte']
