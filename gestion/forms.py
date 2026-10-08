from django import forms
from .models import CommandeFournisseur

class CommandeForm(forms.ModelForm):
    class Meta:
        model = CommandeFournisseur
        fields = ['numero_commande', 'fournisseur', 'magasin', 'statut', 'remarque']
        widgets = {
            'numero_commande': forms.TextInput(attrs={'class': 'form-control'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'magasin': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.TextInput(attrs={'class': 'form-control'}),
            'remarque': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }