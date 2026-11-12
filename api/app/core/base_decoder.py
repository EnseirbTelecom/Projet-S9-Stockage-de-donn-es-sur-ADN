from abc import ABC, abstractmethod

class BaseDecodeur(ABC):

    @abstractmethod
    def decode(self, sequence: str) -> str:
        pass