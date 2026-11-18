
# Canal ADN simple
# Un brin est une chaîne de caractères avec les lettres A, C, G, T.
# On simule 3 types d'erreurs : substitution, insertion, délétion.

import random

from app.core.base_channel import BaseCanal

BASES = "ATCG"


class CanalModele1(BaseCanal):

    def __init__(self, pts, pi, pd):
        if not all(0 <= p <= 1 for p in (pts, pi, pd)):
            raise ValueError("Les probabilités doivent être comprises entre 0 et 1.")

        if pts + pi + pd > 1:
            raise ValueError("La somme des probabilités ne doit pas dépasser 1.")

        self.pts = pts
        self.pi = pi
        self.pd = pd

    def substitution(self, base):
        nouvelle_base = random.choice(BASES)
        while nouvelle_base == base:
            nouvelle_base = random.choice(BASES)
        return nouvelle_base

    def insertion(self, base):
        return random.choice(BASES)

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
            tirage = random.random()

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
