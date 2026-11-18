from abc import ABC, abstractmethod


class BaseCanal(ABC):
    """Contrat commun à tous les modèles de canal de transmission.

    Un canal reçoit une séquence et simule les altérations pouvant
    survenir lors du stockage / de la lecture des molécules ADN.
    """

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
