from app.core.base_channel import BaseCanal


class ChannelWrapper:
    """Interface commune pour manipuler les modèles de canal."""

    def __init__(self, strategy: BaseCanal):
        self.strategy = strategy

    def transmit(self, sequence: str) -> dict:
        return self.strategy.transmit(sequence)
