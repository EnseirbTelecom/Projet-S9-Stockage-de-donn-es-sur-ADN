from app.core.base_encoder import BaseEncodeur

class GrayEncoder(BaseEncodeur):

    slug = "gray"
    name = "Mapping de Gray"
    description = (
        "Convertit chaque paire de bits en une base azotée selon un mapping de Gray :"
        "00 → A\n , 01 → T\n , 11 → C\n et 10 → G\n "
        "La séquence binaire doit être non vide et contenir un "
        "nombre pair de bits."
    )
    parameters = {
        "seed": {
            "type": "integer",
            "default": None,
            "label": "Graine aléatoire (reproductibilité)",
        }
    }
     
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