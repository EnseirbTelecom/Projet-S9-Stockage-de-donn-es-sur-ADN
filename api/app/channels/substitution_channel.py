import random as rd

from app.core.base_channel import BaseCanal

BASES = "ATCG"


class SubstitutionChannel(BaseCanal):
    """Canal à substitutions : chaque base peut être remplacée
    par une autre base (A, T, C ou G) avec une probabilité donnée.

    Modélise les erreurs de synthèse / séquençage de l'ADN.
    """

    slug = "substitution"
    name = "Canal à substitutions"
    description = (
        "Modélise les erreurs de synthèse / séquençage : avec une "
        "probabilité donnée, chaque base est remplacée par une autre base."
    )
    parameters = {
        "error_rate": {
            "type": "number",
            "default": 0.05,
            "min": 0.0,
            "max": 1.0,
            "label": "Taux d'erreur",
        },
        "seed": {
            "type": "integer",
            "default": None,
            "label": "Graine aléatoire (reproductibilité)",
        },
    }

    def __init__(self, error_rate: float = 0.05, seed: int | None = None):
        if not 0 <= error_rate <= 1:
            raise ValueError("Le taux d'erreur doit être compris entre 0 et 1.")

        self.error_rate = error_rate
        self.seed = seed
        self.rng = rd.Random(seed)

    def transmit(self, sequence: str) -> dict:
        if not all(base in BASES for base in sequence):
            raise ValueError("La séquence doit contenir uniquement les bases A, T, C et G.")

        output = []
        errors = []

        for index, base in enumerate(sequence):
            if self.rng.random() < self.error_rate:
                received = self.rng.choice([b for b in BASES if b != base])
                output.append(received)
                errors.append({
                    "index": index,
                    "original": base,
                    "received": received,
                })
            else:
                output.append(base)

        return {
            "output": "".join(output),
            "errors": errors,
        }
