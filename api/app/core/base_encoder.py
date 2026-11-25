from abc import ABC, abstractmethod


class BaseEncodeur(ABC):
    """Contrat commun à tous les encodeurs.

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
    def encode(self, data: str) -> str:
        pass

    @classmethod
    def describe(cls) -> dict:
        """Petit JSON décrivant l'implémentation."""
        return {
            "category": "encoder",
            "slug": cls.slug,
            "name": cls.name,
            "description": cls.description,
            "parameters": dict(cls.parameters),
        }
