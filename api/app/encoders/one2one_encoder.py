import random as rd
from app.core.base_encoder import BaseEncodeur

class One2OneEncoder(BaseEncodeur):

    slug = "one2one"
    name = "One2One : 1 bit -> 1 base"
    description = (
        "Associe à chaque bit une base azotée : 0 devient A ou T, "
        "1 devient C ou G. La base exacte est tirée aléatoirement "
        "(reproductible avec une graine)."
    )
    parameters = {
        "seed": {
            "type": "integer",
            "default": None,
            "label": "Graine aléatoire (reproductibilité)",
        }
    }

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.rng = rd.Random(seed)

    def encode(self, data):
        if not all(bit in "01" for bit in data):
            raise ValueError("La séquence doit contenir uniquement des bits 0 et 1.")

        zero = "AT"
        one = "CG"

        result = []
        for bit in data:
            if bit == "0":
                result.append(self.rng.choice(zero))
            elif bit == "1":
                result.append(self.rng.choice(one))

        return "".join(result)