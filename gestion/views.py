from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView, ListView, TemplateView, UpdateView

from .forms import (
    CommandeFournisseurForm, InscriptionClientForm, LigneCommandeForm, MouvementStockForm,
    ProduitForm, SeuilStockForm, StaffAuthenticationForm, StatutCommandeForm,
)
from .models import (
    Categorie, Commande, CommandeFournisseur, LigneCommande, Livraison, MouvementStock, Produits, Stock,
)
from .stock import StockInsuffisant, enregistrer_mouvement, magasin_vente_en_ligne


# ===========================================================================
# PARTIE PUBLIQUE / CLIENTS
# ===========================================================================
def accueil(request):
    """Catalogue visible par TOUT LE MONDE : seulement le nom, la catégorie et le prix de vente."""
    produits = Produits.objects.filter(actif=True).select_related('categorie')

    recherche = request.GET.get('q', '').strip()
    if recherche:
        produits = produits.filter(Q(nom__icontains=recherche) | Q(description__icontains=recherche))

    categorie_id = request.GET.get('categorie', '')
    if categorie_id.isdigit():
        produits = produits.filter(categorie_id=int(categorie_id))

    # Disponibilité publique = seulement "en stock / rupture" (jamais les quantités exactes),
    # calculée sur le magasin de vente en ligne.
    produits = list(produits.order_by('nom'))
    magasin = magasin_vente_en_ligne()
    dispo = {}
    if magasin:
        dispo = dict(Stock.objects.filter(magasin=magasin).values_list('produit_id', 'quantite'))
    for p in produits:
        p.disponible = dispo.get(p.id, 0) > 0

    return render(request, 'gestion/accueil.html', {
        'produits': produits,
        'categories': Categorie.objects.order_by('nom'),
        'recherche': recherche,
        'categorie_id': categorie_id,
    })


def inscription_client(request):
    """Inscription libre, réservée aux CLIENTS (les comptes staff se créent dans /admin/)."""
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = InscriptionClientForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.username}, votre compte est créé.')
            return redirect('accueil')
    else:
        form = InscriptionClientForm()
    return render(request, 'gestion/inscription.html', {'form': form})


@login_required
def passer_commande(request, produit_id):
    """Un client connecté commande un produit actif, dans la limite du stock disponible."""
    produit = get_object_or_404(Produits, pk=produit_id, actif=True)
    magasin = magasin_vente_en_ligne()
    if magasin is None:
        messages.error(request, "Les commandes sont momentanément indisponibles.")
        return redirect('accueil')

    if request.method == 'POST':
        form = LigneCommandeForm(request.POST)
        if form.is_valid():
            quantite = form.cleaned_data['quantite']
            try:
                # atomic : soit TOUT est enregistré (commande, ligne, sortie de stock), soit RIEN.
                with transaction.atomic():
                    commande = Commande.objects.create(client=request.user)
                    LigneCommande.objects.create(
                        commande=commande,
                        produit=produit,
                        quantite=quantite,
                        # Le prix vient de la base de données, JAMAIS du navigateur.
                        prix_unitaire=produit.prix_vente,
                    )
                    enregistrer_mouvement(
                        produit=produit, magasin=magasin, type_mouvement=MouvementStock.Type.SORTIE,
                        quantite=quantite, auteur=request.user,
                        motif=f'Commande client #{commande.pk}', commande_client=commande)
            except StockInsuffisant as erreur:
                # L'exception a annulé la transaction : aucune commande n'a été créée.
                form.add_error('quantite', str(erreur))
            else:
                messages.success(request, f'Commande #{commande.pk} enregistrée.')
                return redirect('mes_commandes')
    else:
        form = LigneCommandeForm()
    return render(request, 'gestion/passer_commande.html', {'produit': produit, 'form': form})


@login_required
def mes_commandes(request):
    """Un client ne voit QUE ses propres commandes (filtre sur request.user)."""
    commandes = (Commande.objects.filter(client=request.user)
                 .prefetch_related('lignes__produit'))
    return render(request, 'gestion/mes_commandes.html', {'commandes': commandes})


# ===========================================================================
# ESPACE GESTION (STAFF UNIQUEMENT)
# ===========================================================================
class StaffLoginView(LoginView):
    """Page de connexion de l'espace gestion (refuse les non-staff, voir le formulaire)."""
    authentication_form = StaffAuthenticationForm
    template_name = 'gestion/login.html'
    redirect_authenticated_user = False
    extra_context = {'staff': True}

    def get_success_url(self):
        return self.get_redirect_url() or reverse('tableau_de_bord')


class GestionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Règle commune à TOUTES les pages de gestion :
      1. il faut être connecté (sinon -> page de connexion gestion)
      2. il faut être staff
      3. il faut avoir la permission demandée par la vue (permission_required)
    Connecté mais sans droit -> erreur 403 "Accès refusé".
    """
    login_url = reverse_lazy('gestion_login')
    permission_required = ()

    def has_permission(self):
        return self.request.user.is_staff and super().has_permission()


class TableauDeBord(GestionMixin, TemplateView):
    template_name = 'gestion/tableau_de_bord.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # On ne charge que ce que la personne a le droit de voir.
        if user.has_perm('gestion.view_commandefournisseur'):
            ctx['commandes'] = CommandeFournisseur.objects.select_related('fournisseur').order_by('-date_commande')[:10]
        if user.has_perm('gestion.view_livraison'):
            ctx['livraisons'] = Livraison.objects.select_related('commande').order_by('-date_livraison')[:10]
        if user.has_perm('gestion.view_stock'):
            ctx['nb_alertes'] = Stock.objects.filter(quantite__lte=F('seuil_alerte')).count()
            ctx['magasin_en_ligne_manquant'] = magasin_vente_en_ligne() is None
        return ctx


class ProduitListe(GestionMixin, ListView):
    permission_required = 'gestion.view_produits'
    model = Produits
    template_name = 'gestion/produit_liste.html'
    context_object_name = 'produits'
    queryset = Produits.objects.select_related('categorie', 'marque').order_by('nom')
    paginate_by = 25


class ProduitCreer(GestionMixin, CreateView):
    permission_required = 'gestion.add_produits'
    form_class = ProduitForm
    template_name = 'gestion/form_generique.html'
    success_url = reverse_lazy('produit_liste')
    extra_context = {'titre': 'Nouveau produit', 'retour': reverse_lazy('produit_liste')}

    def form_valid(self, form):
        messages.success(self.request, 'Produit ajouté.')
        return super().form_valid(form)


class ProduitModifier(GestionMixin, UpdateView):
    permission_required = 'gestion.change_produits'
    model = Produits
    form_class = ProduitForm
    template_name = 'gestion/form_generique.html'
    success_url = reverse_lazy('produit_liste')
    extra_context = {'titre': 'Modifier le produit', 'retour': reverse_lazy('produit_liste')}

    def form_valid(self, form):
        messages.success(self.request, 'Produit modifié.')
        return super().form_valid(form)


class CommandeFournisseurCreer(GestionMixin, CreateView):
    permission_required = 'gestion.add_commandefournisseur'
    form_class = CommandeFournisseurForm
    template_name = 'gestion/form_generique.html'
    success_url = reverse_lazy('tableau_de_bord')
    extra_context = {'titre': 'Enregistrer une commande fournisseur', 'retour': reverse_lazy('tableau_de_bord')}

    def form_valid(self, form):
        # Le champ "cree_par" n'est pas dans le formulaire : on le remplit côté serveur.
        form.instance.cree_par = self.request.user.username
        messages.success(self.request, 'Commande fournisseur enregistrée.')
        return super().form_valid(form)


class CommandeClientListe(GestionMixin, ListView):
    permission_required = 'gestion.view_commande'
    template_name = 'gestion/commande_client_liste.html'
    context_object_name = 'commandes'
    queryset = Commande.objects.select_related('client').prefetch_related('lignes__produit')
    paginate_by = 25


class CommandeClientStatut(GestionMixin, UpdateView):
    permission_required = 'gestion.change_commande'
    model = Commande
    form_class = StatutCommandeForm
    template_name = 'gestion/form_generique.html'
    success_url = reverse_lazy('commande_client_liste')
    extra_context = {'titre': 'Changer le statut de la commande', 'retour': reverse_lazy('commande_client_liste')}

    def form_valid(self, form):
        ancien = form.initial.get('statut')
        commande = form.instance
        with transaction.atomic():
            response = super().form_valid(form)
            if commande.statut == Commande.Statut.ANNULEE and ancien != Commande.Statut.ANNULEE:
                # Annulation : on remet en stock exactement ce que la commande avait sorti.
                sorties = MouvementStock.objects.filter(
                    commande_client=commande, type_mouvement=MouvementStock.Type.SORTIE)
                for sortie in sorties:
                    enregistrer_mouvement(
                        produit=sortie.produit, magasin=sortie.magasin,
                        type_mouvement=MouvementStock.Type.ENTREE, quantite=sortie.quantite,
                        auteur=self.request.user, motif=f'Annulation commande #{commande.pk}',
                        commande_client=commande)
        messages.success(self.request, 'Statut mis à jour.')
        return response


# --- Stock ------------------------------------------------------------------
class StockListe(GestionMixin, ListView):
    permission_required = 'gestion.view_stock'
    template_name = 'gestion/stock_liste.html'
    context_object_name = 'stocks'
    paginate_by = 25

    def get_queryset(self):
        qs = Stock.objects.select_related('produit', 'magasin')
        if self.request.GET.get('alerte') == '1':
            qs = qs.filter(quantite__lte=F('seuil_alerte'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtre_alerte'] = self.request.GET.get('alerte') == '1'
        return ctx


class StockSeuil(GestionMixin, UpdateView):
    permission_required = 'gestion.change_stock'
    model = Stock
    form_class = SeuilStockForm
    template_name = 'gestion/form_generique.html'
    success_url = reverse_lazy('stock_liste')
    extra_context = {'titre': "Modifier le seuil d'alerte", 'retour': reverse_lazy('stock_liste')}

    def form_valid(self, form):
        messages.success(self.request, "Seuil d'alerte mis à jour.")
        return super().form_valid(form)


class MouvementCreer(GestionMixin, FormView):
    permission_required = 'gestion.add_mouvementstock'
    form_class = MouvementStockForm
    template_name = 'gestion/form_generique.html'
    success_url = reverse_lazy('stock_liste')
    extra_context = {'titre': 'Enregistrer un mouvement de stock', 'retour': reverse_lazy('stock_liste')}

    def form_valid(self, form):
        d = form.cleaned_data
        try:
            enregistrer_mouvement(
                produit=d['produit'], magasin=d['magasin'], type_mouvement=d['type_mouvement'],
                quantite=d['quantite'], auteur=self.request.user, motif=d['motif'])
        except StockInsuffisant as erreur:
            form.add_error('quantite', str(erreur))
            return self.form_invalid(form)
        messages.success(self.request, 'Mouvement enregistré.')
        return super().form_valid(form)


class MouvementListe(GestionMixin, ListView):
    permission_required = 'gestion.view_mouvementstock'
    template_name = 'gestion/mouvement_liste.html'
    context_object_name = 'mouvements'
    queryset = MouvementStock.objects.select_related('produit', 'magasin', 'auteur')
    paginate_by = 25
