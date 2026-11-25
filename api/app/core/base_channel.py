from abc import ABC, abstractmethod


class BaseCanal(ABC):
    """Contrat commun à tous les modèles de canal de transmission.

    Un canal reçoit une séquence et simule les altérations pouvant
    survenir lors du stockage / de la lecture des molécules ADN.

    Toute implémentation se décrit via les attributs de classe
    `slug`, `name`, `description` et `parameters`. Le petit JSON
    correspondant (`describe()`) est exposé par GET /catalog et
    consommé par le site web pour rester adaptable.
    """

    slug = ""
    name = ""
    description = ""
    parameters = {}

    @abstractmethod
    def transmit(self, sequence: str) -> dict:
        """Transmet la séquence dans le canal.

        Args:
            sequence: séquence d'entrée du canal.

        Returns:
            dict: dictionnaire contenant au minimum :
                - "output" (str): la séquence reçue après transmission ;
                - "errors" (list[dict]): la liste des altérations
                  introduites par le canal.
        """
        pass

    @classmethod
    def describe(cls) -> dict:
        """Petit JSON décrivant l'implémentation."""
        return {
            "category": "channel",
            "slug": cls.slug,
            "name": cls.name,
            "description": cls.description,
            "parameters": dict(cls.parameters),
        }
