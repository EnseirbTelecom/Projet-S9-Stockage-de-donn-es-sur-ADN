import random as rd
from app.core.base_encoder import BaseEncodeur

class One2OneEncoder(BaseEncodeur):

    def encode(self, data):
        if not all(bit in "01" for bit in data):
            raise ValueError("La séquence doit contenir uniquement des bits 0 et 1.")

        zero = "AT"
        one = "CG"

        result = []
        for bit in data:
            if bit == "0":
                result.append(rd.choice(zero))
            elif bit == "1":
                result.append(rd.choice(one))

        return "".join(result)