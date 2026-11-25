from app.core.base_decoder import BaseDecodeur

class One2OneDecoder(BaseDecodeur):

    slug = "one2one"
    name = "One2One : 1 base -> 1 bit"
    description = (
        "Convertit chaque base en bit : A ou T valent 0, C ou G valent 1."
    )
    parameters = {}

    def decode(self, sequence):
        result = []
        for base in sequence:
            if base in "AT":
                result.append("0")
            elif base in "CG":
                result.append("1")

        return "".join(result)