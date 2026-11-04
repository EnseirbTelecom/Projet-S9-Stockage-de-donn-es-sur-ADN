from abc import ABC, abstractmethod

class BaseEncodeur(ABC):

    @abstractmethod
    def encode(self, data: str) -> str:
        pass