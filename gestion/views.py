from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CommandeFournisseur, Livraison, Produits
from .forms import CommandeForm

@login_required
def tableau_de_bord(request):
    commandes = CommandeFournisseur.objects.all().order_by('-date_commande')
    livraisons = Livraison.objects.all().order_by('-date_livraison')
    return render(request, 'gestion/tableau_de_bord.html', {
        'commandes': commandes,
        'livraisons': livraisons,
    })
    
@login_required
def creer_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.cree_par = request.user.username
            commande.save()
            return redirect('tableau_de_bord')
    else:
        form = CommandeForm()
    
    return render(request, 'gestion/creer_commande.html', {'form': form})    