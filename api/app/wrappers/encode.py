from app.core.base_encoder import BaseEncodeur

class EncodeWrapper:

    def __init__(self, strategy: BaseEncodeur):
        self.strategy = strategy

    def encode(self, data: str) -> str:
        return self.strategy.encode(data)