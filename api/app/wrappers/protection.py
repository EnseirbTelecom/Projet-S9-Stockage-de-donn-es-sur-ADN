from app.core.base_protection import BaseProtection


class ProtectionWrapper:
    """Interface commune pour manipuler les mécanismes de protection."""

    def __init__(self, strategy: BaseProtection):
        self.strategy = strategy

    def protect(self, data: str) -> str:
        return self.strategy.protect(data)

    def restore(self, data: str) -> dict:
        return self.strategy.restore(data)
