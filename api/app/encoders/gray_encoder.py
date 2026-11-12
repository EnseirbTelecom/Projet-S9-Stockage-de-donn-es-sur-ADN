from app.core.base_encoder import BaseEncodeur

class GrayEncoder(BaseEncodeur):
     
    def encode(self, data):

        # Dictionnaire pour le mapping de Gray
        mapping ={"00":"A", "01":"T", "11":"C", "10":"G"}
        
        ## Pretraitement du code binaire en entree
        
        # Tests robustesse chaine en entrée
        if len(data) == 0:
            raise ValueError("La séquence en entrée est vide")


        if not set(data).issubset({"0", "1"}):
            raise ValueError("La sequence doit contenir uniquement des bits 0 et 1.")

        # Test que le nombre de bits est pair
        if len(data) % 2 != 0:
            raise ValueError("Le nombre de bits doit etre pair.")

        sequence_adn = ""

        # Parcours de la chaine binaire
        for i in range(0, len(data), 2):

            pair = data[i:i+2]

            # Conversion de la paire binaire caracteres adn
            sequence_adn += mapping[pair]

        return sequence_adn