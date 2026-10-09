from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Categorie, Commande, CommandeFournisseur, Fournisseur, Magasin, Produits

User = get_user_model()


class BaseTestCase(TestCase):
    """Prépare des données communes avant CHAQUE test (la base de test est vidée à chaque fois)."""

    @classmethod
    def setUpTestData(cls):
        call_command('creer_roles')  # crée les groupes de rôles
        cls.cat = Categorie.objects.create(nom='Boissons')
        cls.p_actif = Produits.objects.create(
            code_produit='P1', nom='Jus d\'orange', prix_achat=Decimal('400'), prix_vente=Decimal('600'),
            categorie=cls.cat, unite_mesure='L', taux_tva=Decimal('19.25'))
        cls.p_inactif = Produits.objects.create(
            code_produit='P2', nom='Produit retiré', prix_achat=Decimal('100'), prix_vente=Decimal('150'),
            categorie=cls.cat, unite_mesure='u', taux_tva=Decimal('0'), actif=False)
        cls.client_user = User.objects.create_user('alice', 'alice@ex.com', 'MotDePasse!2026x')
        cls.gest_stock = User.objects.create_user('stockiste', password='MotDePasse!2026x', is_staff=True)
        cls.gest_stock.groups.add(Group.objects.get(name='Gestionnaire de stock'))
        cls.vendeur = User.objects.create_user('vendeur', password='MotDePasse!2026x', is_staff=True)
        cls.vendeur.groups.add(Group.objects.get(name='Vendeur'))
        cls.staff_sans_droit = User.objects.create_user('nouveau', password='MotDePasse!2026x', is_staff=True)


class CataloguePublicTests(BaseTestCase):
    def test_visiteur_voit_nom_et_prix(self):
        r = self.client.get(reverse('accueil'))
        self.assertContains(r, "Jus d&#x27;orange")
        self.assertContains(r, '600')

    def test_prix_achat_et_produits_inactifs_caches(self):
        r = self.client.get(reverse('accueil'))
        self.assertNotContains(r, 'Produit retiré')
        self.assertNotContains(r, '400')

    def test_recherche(self):
        r = self.client.get(reverse('accueil'), {'q': 'zzz'})
        self.assertContains(r, 'Aucun produit trouvé')


class InscriptionEtCommandeTests(BaseTestCase):
    def test_inscription_cree_un_client_non_staff(self):
        r = self.client.post(reverse('inscription'), {
            'username': 'bob', 'email': 'bob@ex.com',
            'password1': 'UnMotDePasse!Solide2026', 'password2': 'UnMotDePasse!Solide2026',
            # Tentative de triche : un pirate ajoute ces champs à la main
            'is_staff': 'on', 'is_superuser': 'on',
        })
        self.assertRedirects(r, reverse('accueil'))
        bob = User.objects.get(username='bob')
        self.assertFalse(bob.is_staff)
        self.assertFalse(bob.is_superuser)

    def test_email_deja_utilise_refuse(self):
        r = self.client.post(reverse('inscription'), {
            'username': 'autre', 'email': 'ALICE@ex.com',
            'password1': 'UnMotDePasse!Solide2026', 'password2': 'UnMotDePasse!Solide2026'})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='autre').exists())

    def test_commande_exige_connexion(self):
        url = reverse('passer_commande', args=[self.p_actif.id])
        r = self.client.get(url)
        self.assertRedirects(r, f"{reverse('login')}?next={url}")

    def test_commande_enregistre_le_prix_du_serveur(self):
        self.client.force_login(self.client_user)
        r = self.client.post(reverse('passer_commande', args=[self.p_actif.id]),
                             {'quantite': 3, 'prix_unitaire': '1'})  # prix truqué ignoré
        self.assertRedirects(r, reverse('mes_commandes'))
        cmd = Commande.objects.get(client=self.client_user)
        self.assertEqual(cmd.lignes.get().prix_unitaire, Decimal('600.00'))
        self.assertEqual(cmd.total, Decimal('1800.00'))

    def test_quantite_invalide_refusee(self):
        self.client.force_login(self.client_user)
        for q in ('0', '-2', 'abc', '100000'):
            self.client.post(reverse('passer_commande', args=[self.p_actif.id]), {'quantite': q})
        self.assertEqual(Commande.objects.count(), 0)

    def test_produit_inactif_non_commandable(self):
        self.client.force_login(self.client_user)
        r = self.client.get(reverse('passer_commande', args=[self.p_inactif.id]))
        self.assertEqual(r.status_code, 404)

    def test_un_client_ne_voit_que_ses_commandes(self):
        autre = User.objects.create_user('carl', password='MotDePasse!2026x')
        Commande.objects.create(client=autre)
        r = self.client.get(reverse('mes_commandes'))  # non connecté
        self.assertEqual(r.status_code, 302)
        self.client.force_login(self.client_user)
        r = self.client.get(reverse('mes_commandes'))
        self.assertEqual(len(r.context['commandes']), 0)


class EspaceGestionTests(BaseTestCase):
    def test_visiteur_redirige_vers_connexion_gestion(self):
        r = self.client.get(reverse('tableau_de_bord'))
        self.assertRedirects(r, f"{reverse('gestion_login')}?next={reverse('tableau_de_bord')}")

    def test_client_connecte_a_acces_refuse(self):
        self.client.force_login(self.client_user)
        for nom in ('tableau_de_bord', 'produit_liste', 'commande_client_liste'):
            self.assertEqual(self.client.get(reverse(nom)).status_code, 403, nom)

    def test_connexion_gestion_refuse_un_client(self):
        r = self.client.post(reverse('gestion_login'), {'username': 'alice', 'password': 'MotDePasse!2026x'})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_connexion_gestion_accepte_le_staff(self):
        r = self.client.post(reverse('gestion_login'), {'username': 'stockiste', 'password': 'MotDePasse!2026x'})
        self.assertRedirects(r, reverse('tableau_de_bord'))

    def test_staff_sans_droit_voit_le_tableau_mais_pas_les_pages(self):
        self.client.force_login(self.staff_sans_droit)
        r = self.client.get(reverse('tableau_de_bord'))
        self.assertContains(r, 'Aucun droit')
        self.assertEqual(self.client.get(reverse('produit_liste')).status_code, 403)

    def test_gestionnaire_stock_peut_creer_un_produit(self):
        self.client.force_login(self.gest_stock)
        r = self.client.post(reverse('produit_creer'), {
            'code_produit': 'P3', 'nom': 'Eau', 'prix_achat': '100', 'prix_vente': '200',
            'categorie': self.cat.id, 'unite_mesure': 'L', 'taux_tva': '0', 'actif': 'on'})
        self.assertRedirects(r, reverse('produit_liste'))
        self.assertTrue(Produits.objects.filter(code_produit='P3').exists())

    def test_vendeur_ne_peut_pas_creer_un_produit_mais_voit_les_commandes(self):
        self.client.force_login(self.vendeur)
        self.assertEqual(self.client.get(reverse('produit_creer')).status_code, 403)
        self.assertEqual(self.client.get(reverse('commande_client_liste')).status_code, 200)

    def test_vendeur_peut_changer_le_statut_mais_pas_gestionnaire_stock(self):
        cmd = Commande.objects.create(client=self.client_user)
        url = reverse('commande_client_statut', args=[cmd.pk])
        self.client.force_login(self.gest_stock)
        self.assertEqual(self.client.post(url, {'statut': 'LIVREE'}).status_code, 403)
        self.client.force_login(self.vendeur)
        self.client.post(url, {'statut': 'LIVREE'})
        cmd.refresh_from_db()
        self.assertEqual(cmd.statut, 'LIVREE')

    def test_commande_fournisseur_remplit_cree_par(self):
        resp_achats = User.objects.create_user('achats', password='MotDePasse!2026x', is_staff=True)
        resp_achats.groups.add(Group.objects.get(name='Responsable achats'))
        f = Fournisseur.objects.create(nom='SABC')
        m = Magasin.objects.create(code_magasin='M1', nom='Douala centre')
        self.client.force_login(resp_achats)
        r = self.client.post(reverse('creer_commande'), {
            'numero_commande': 'CF-001', 'fournisseur': f.id, 'magasin': m.id, 'statut': 'BROUILLON'})
        self.assertRedirects(r, reverse('tableau_de_bord'))
        self.assertEqual(CommandeFournisseur.objects.get().cree_par, 'achats')

    def test_creer_roles_est_repetable(self):
        call_command('creer_roles')
        call_command('creer_roles')
        self.assertEqual(Group.objects.filter(name='Vendeur').count(), 1)

    def test_deconnexion_en_post_seulement(self):
        self.client.force_login(self.client_user)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
