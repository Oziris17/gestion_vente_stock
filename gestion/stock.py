"""
Logique du stock. TOUTE modification de quantité passe par `enregistrer_mouvement` :
c'est ce qui garantit qu'aucune quantité ne change sans laisser une trace dans l'historique.
"""
from decimal import Decimal

from django.db import transaction

from .models import Magasin, MouvementStock, Stock


class StockInsuffisant(Exception):
    """Levée quand une sortie dépasse la quantité disponible."""


def _propre(d):
    """12.000 -> '12' ; 2.500 -> '2.5' (affichage dans les messages)."""
    return format(d.normalize(), 'f')


def magasin_vente_en_ligne():
    return Magasin.objects.filter(actif=True, vente_en_ligne=True).first()


def enregistrer_mouvement(*, produit, magasin, type_mouvement, quantite, auteur=None,
                          motif='', commande_client=None):
    quantite = Decimal(quantite)
    # atomic : si une erreur survient, ni le stock ni le journal ne sont modifiés.
    with transaction.atomic():
        stock, _ = Stock.objects.get_or_create(produit=produit, magasin=magasin)
        # select_for_update verrouille la ligne : deux commandes simultanées ne peuvent pas
        # consommer le même stock en même temps.
        stock = Stock.objects.select_for_update().get(pk=stock.pk)
        avant = stock.quantite

        if type_mouvement == MouvementStock.Type.ENTREE:
            apres = avant + quantite
        elif type_mouvement == MouvementStock.Type.SORTIE:
            apres = avant - quantite
            if apres < 0:
                raise StockInsuffisant(f"Stock insuffisant : {_propre(avant)} disponible(s).")
        elif type_mouvement == MouvementStock.Type.AJUSTEMENT:
            apres = quantite
        else:
            raise ValueError(f"Type de mouvement inconnu : {type_mouvement}")

        stock.quantite = apres
        stock.save(update_fields=['quantite'])
        return MouvementStock.objects.create(
            produit=produit, magasin=magasin, type_mouvement=type_mouvement, quantite=quantite,
            quantite_avant=avant, quantite_apres=apres, motif=motif,
            commande_client=commande_client, auteur=auteur,
        )
