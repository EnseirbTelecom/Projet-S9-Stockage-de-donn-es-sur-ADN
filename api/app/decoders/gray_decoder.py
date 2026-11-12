from app.core.base_decoder import BaseDecodeur

class GrayDecoder(BaseDecodeur):

    def decode(self, sequence):
        # Mapping inverse
        inverse_mapping = {"A": "00", "T": "01", "C": "11", "G": "10"}

        bits = ""

        for nucleotide in sequence:

            if nucleotide not in inverse_mapping:
                raise ValueError("Décodage impossible : Caractère erroné")

            bits += inverse_mapping[nucleotide]

        return bits
