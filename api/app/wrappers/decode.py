from app.core.base_decoder import BaseDecodeur

class DecodeWrapper:

    def __init__(self, strategy: BaseDecodeur):
        self.strategy = strategy

    def decode(self, sequence: str) -> str:
        return self.strategy.decode(sequence)