"""Registre central des implémentations de la chaîne de transmission.

Pour rendre une nouvelle implémentation disponible dans l'API et le site :

1. créer la classe dans son dossier (`encoders/`, `decoders/`, `channels/`,
   `protections/`, ...), hériter de la classe abstraite de sa catégorie et
   renseigner les attributs de classe `slug`, `name`, `description` et
   `parameters` (le petit JSON de description) ;
2. ajouter la classe au dictionnaire de sa catégorie dans `REGISTRY`.

`GET /catalog` expose ensuite automatiquement le JSON de description de
chaque implémentation, qui est consommé par le site web.
"""
import inspect

from app.encoders.one2one_encoder import One2OneEncoder
from app.decoders.one2one_decoder import One2OneDecoder
from app.channels.substitution_channel import SubstitutionChannel
from app.protections.replication_protection import ReplicationProtection

REGISTRY = {
    "encoder": {
        "one2one": One2OneEncoder,
    },
    "decoder": {
        "one2one": One2OneDecoder,
    },
    "channel": {
        "substitution": SubstitutionChannel,
    },
    "protection": {
        "replication": ReplicationProtection,
    },
}


def get_strategy(category: str, slug: str):
    """Retourne la classe d'implémentation demandée.

    Raises:
        ValueError: si la catégorie ou le slug est inconnu.
    """
    try:
        return REGISTRY[category][slug]
    except KeyError:
        available = (
            ", ".join(sorted(REGISTRY[category]))
            if category in REGISTRY
            else f"catégorie '{category}' inexistante"
        )
        raise ValueError(
            f"Stratégie '{slug}' inconnue pour la catégorie '{category}'. "
            f"Choix possibles : {available}."
        )


def build_strategy(category: str, slug: str, **kwargs):
    """Instancie l'implémentation de manière générique.

    Seuls les paramètres réellement acceptés par le constructeur de la
    classe sont passés : le site (ou la chaîne) peut transmettre des
    paramètres en surplus sans que cela ne casse les implémentations
    dont ils ne sont pas pertinents.
    """
    cls = get_strategy(category, slug)
    accepted = inspect.signature(cls.__init__).parameters
    filtered = {name: value for name, value in kwargs.items() if name in accepted}
    return cls(**filtered)
