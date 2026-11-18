from app.core.base_protection import BaseProtection

BASES = "ATCG"


class ReplicationProtection(BaseProtection):
    """Protection par réplication : chaque base est répétée `factor` fois
    avant transmission. À la réception, un vote majoritaire par bloc
    corrige les substitutions isolées.
    """

    slug = "replication"
    name = "Réplication + vote majoritaire"
    description = (
        "Répète chaque base un nombre impair de fois avant transmission ; "
        "à la réception, la base majoritaire de chaque bloc est conservée, "
        "ce qui corrige les substitutions isolées."
    )
    parameters = {
        "factor": {
            "type": "integer",
            "default": 3,
            "min": 3,
            "label": "Facteur de réplication (impair >= 3)",
        }
    }

    def __init__(self, factor: int = 3):
        if factor < 3 or factor % 2 == 0:
            raise ValueError("Le facteur de réplication doit être un entier impair >= 3.")

        self.factor = factor

    def protect(self, data: str) -> str:
        if not all(base in BASES for base in data):
            raise ValueError("La séquence doit contenir uniquement les bases A, T, C et G.")

        return "".join(base * self.factor for base in data)

    def restore(self, data: str) -> dict:
        if len(data) % self.factor != 0:
            raise ValueError(
                "La taille de la séquence doit être un multiple du facteur de réplication."
            )

        output = []
        corrections = []

        for block_index in range(len(data) // self.factor):
            block = data[block_index * self.factor:(block_index + 1) * self.factor]

            # Vote majoritaire sur le bloc
            counts = {base: block.count(base) for base in set(block)}
            consensus = max(counts, key=counts.get)
            output.append(consensus)

            for offset, base in enumerate(block):
                if base != consensus:
                    corrections.append({
                        "block": block_index,
                        "index": block_index * self.factor + offset,
                        "received": base,
                        "corrected": consensus,
                    })

        return {
            "output": "".join(output),
            "corrections": corrections,
        }
