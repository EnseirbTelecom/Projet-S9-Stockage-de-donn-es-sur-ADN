from abc import ABC, abstractmethod


class BaseProtection(ABC):
    """Contrat commun à tous les mécanismes de protection de la séquence.

    Un mécanisme de protection redondante ajoutée avant la transmission
    (protection) puis exploitée après réception pour détecter / corriger
    des erreurs (restauration).
    """

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
