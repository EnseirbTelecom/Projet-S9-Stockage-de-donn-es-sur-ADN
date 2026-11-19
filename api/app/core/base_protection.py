from abc import ABC, abstractmethod


class BaseProtection(ABC):
    """Contrat commun à tous les mécanismes de protection de la séquence.

    Un mécanisme de protection ajoute de la redondance avant la
    transmission (protection) puis l'exploite après réception pour
    détecter / corriger des erreurs (restauration).

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
    def protect(self, data: str) -> str:
        """Ajoute la redondance de protection à la séquence."""
        pass

    @abstractmethod
    def restore(self, data: str) -> dict:
        """Exploite la redondance pour restaurer la séquence d'origine.

        Args:
            data: séquence reçue, avec redondance.

        Returns:
            dict: dictionnaire contenant au minimum :
                - "output" (str): la séquence restaurée ;
                - "corrections" (list[dict]): la liste des corrections
                  appliquées.
        """
        pass

    @classmethod
    def describe(cls) -> dict:
        """Petit JSON décrivant l'implémentation."""
        return {
            "category": "protection",
            "slug": cls.slug,
            "name": cls.name,
            "description": cls.description,
            "parameters": dict(cls.parameters),
        }
