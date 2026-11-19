
# Canal ADN simple
# Un brin est une chaîne de caractères avec les lettres A, C, G, T.
# On simule 3 types d'erreurs : substitution, insertion, délétion.

import random

from app.core.base_channel import BaseCanal

BASES = "ATCG"


class CanalModele1(BaseCanal):

    slug = "modele1"
    name = "Canal modèle 1"
    description = (
        "Modélise les erreurs de transmission d'un canal ADN : avec des "
        "probabilités données, chaque base peut subir une insertion d'une "
        "nouvelle base avant elle, une suppression (deletion), une "
        "substitution par une autre base ou être transmise sans erreur."
    )
    parameters = {
        "pts": {
            "type": "number",
            "default": 0.01,
            "min": 0.0,
            "max": 1.0,
            "label": "Probabilité de substitution",
        },
        "pi": {
            "type": "number",
            "default": 0.01,
            "min": 0.0,
            "max": 1.0,
            "label": "Probabilité d'insertion",
        },
        "pd": {
            "type": "number",
            "default": 0.01,
            "min": 0.0,
            "max": 1.0,
            "label": "Probabilité de suppression",
        },
        "seed": {
            "type": "integer",
            "default": None,
            "label": "Graine aléatoire (reproductibilité)",
        },
    }

    def __init__(self, pts=0.01, pi=0.01, pd=0.01, seed=None):
        if not all(0 <= p <= 1 for p in (pts, pi, pd)):
            raise ValueError("Les probabilités doivent être comprises entre 0 et 1.")

        if pts + pi + pd > 1:
            raise ValueError("La somme des probabilités ne doit pas dépasser 1.")

        self.pts = pts
        self.pi = pi
        self.pd = pd
        self.rng = random.Random(seed)

    def substitution(self, base):
        nouvelle_base = self.rng.choice(BASES)
        while nouvelle_base == base:
            nouvelle_base = self.rng.choice(BASES)
        return nouvelle_base

    def insertion(self, base):
        return self.rng.choice(BASES)

    def deletion(self, base):
        return ""

    def transmit(self, sequence: str) -> dict:

        if not all(base in BASES for base in sequence):
            raise ValueError("La séquence doit contenir uniquement les bases A, T, C et G.")

        nouveau_brin = ""
        errors = []
        i = 0

        while i < len(sequence):
            base = sequence[i]
            tirage = self.rng.random()

            if tirage < self.pi:
                nouvelle_base = self.insertion(base)
                nouveau_brin += nouvelle_base
                nouveau_brin += base

                errors.append({
                    "index": i,
                    "type": "insertion",
                    "original": base,
                    "received": nouvelle_base + base
                })

            elif tirage < self.pi + self.pd:
                nouveau_brin += self.deletion(base)

                errors.append({
                    "index": i,
                    "type": "deletion",
                    "original": base,
                    "received": ""
                })

            elif tirage < self.pi + self.pd + self.pts:
                nouvelle_base = self.substitution(base)
                nouveau_brin += nouvelle_base

                errors.append({
                    "index": i,
                    "type": "substitution",
                    "original": base,
                    "received": nouvelle_base
                })

            else:
                nouveau_brin += base

            i += 1

        return {
            "output": nouveau_brin,
            "errors": errors
        }
