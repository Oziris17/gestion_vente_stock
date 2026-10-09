from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# Chaque rôle = un GROUPE Django + la liste des actions autorisées sur chaque table.
# Actions possibles : view (voir), add (ajouter), change (modifier), delete (supprimer)
ROLES = {
    'Gestionnaire de stock': {
        'produits': ['view', 'add', 'change'],
        'categorie': ['view', 'add', 'change'],
        'marque': ['view', 'add', 'change'],
    },
    'Responsable achats': {
        'fournisseur': ['view', 'add', 'change'],
        'commandefournisseur': ['view', 'add', 'change'],
        'lignecommandefournisseur': ['view', 'add', 'change'],
        'livraison': ['view', 'add', 'change'],
        'lignelivraison': ['view', 'add', 'change'],
        'produits': ['view'],
    },
    'Vendeur': {
        'produits': ['view'],
        'commande': ['view', 'change'],
        'lignecommande': ['view'],
    },
}


class Command(BaseCommand):
    help = "Crée (ou met à jour) les groupes de rôles du personnel. Peut être relancée sans risque."

    def handle(self, *args, **options):
        for nom_role, modeles in ROLES.items():
            groupe, _ = Group.objects.get_or_create(name=nom_role)
            permissions = []
            for modele, actions in modeles.items():
                for action in actions:
                    permissions.append(
                        Permission.objects.get(content_type__app_label='gestion', codename=f'{action}_{modele}')
                    )
            groupe.permissions.set(permissions)  # remplace par la liste exacte
            self.stdout.write(self.style.SUCCESS(f'Rôle « {nom_role} » : {len(permissions)} permissions'))
