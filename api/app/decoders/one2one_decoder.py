from app.core.base_decoder import BaseDecodeur

class One2OneDecoder(BaseDecodeur):

    def decode(self, sequence):
        result = []
        for base in sequence:
            if base in "AT":
                result.append("0")
            elif base in "CG":
                result.append("1")

        return "".join(result)