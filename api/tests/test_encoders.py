import pytest

from app.core.base_encoder import BaseEncodeur
from app.encoders.one2one_encoder import One2OneEncoder
from app.wrappers.encode import EncodeWrapper


@pytest.fixture
def encoder():
    return One2OneEncoder()


@pytest.fixture
def wrapper(encoder):
    return EncodeWrapper(encoder)


class TestOne2OneEncoder:
    def test_herite_de_la_classe_abstraite(self, encoder):
        assert isinstance(encoder, BaseEncodeur)

    def test_zero_devient_a_ou_t(self, encoder):
        result = encoder.encode("00000")
        assert len(result) == 5
        assert all(base in "AT" for base in result)

    def test_un_devient_c_ou_g(self, encoder):
        result = encoder.encode("11111")
        assert len(result) == 5
        assert all(base in "CG" for base in result)

    def test_chaque_bit_est_converti(self, encoder):
        result = encoder.encode("01101")
        attendu = [
            result[0] in "AT",
            result[1] in "CG",
            result[2] in "CG",
            result[3] in "AT",
            result[4] in "CG",
        ]
        assert all(attendu)

    def test_longueur_conservee(self, encoder):
        bits = "010011000111"
        assert len(encoder.encode(bits)) == len(bits)

    def test_sequence_vide(self, encoder):
        assert encoder.encode("") == ""

    def test_erreur_sur_entree_invalide(self, encoder):
        with pytest.raises(ValueError):
            encoder.encode("012")

    def test_erreur_sur_texte_brut(self, encoder):
        with pytest.raises(ValueError):
            encoder.encode("ADN")

    def test_n_accepte_que_des_bits(self, encoder):
        """Un moteur ne doit pas accepter autre chose que des bits."""
        with pytest.raises(ValueError):
            encoder.encode(encoder.encode("0101"))


class TestEncodeWrapper:
    def test_delegue_a_la_strategie(self):
        # Deux encodeurs identiques (même graine) donnent la même sortie
        wrapper = EncodeWrapper(One2OneEncoder(seed=9))
        encoder = One2OneEncoder(seed=9)
        assert wrapper.encode("01011") == encoder.encode("01011")

    def test_resultat_conforme_au_contrat(self, wrapper):
        for bits, bases in [("0", "AT"), ("1", "CG")]:
            result = wrapper.encode(bits)
            assert len(result) == 1
            assert result[0] in bases

    def test_reproductibilite_avec_seed(self):
        encoder1 = One2OneEncoder(seed=5)
        encoder2 = One2OneEncoder(seed=5)
        assert encoder1.encode("01011") == encoder2.encode("01011")

    def test_expose_la_strategie(self, wrapper, encoder):
        assert wrapper.strategy is encoder

    def test_valide_via_la_strategie(self, wrapper):
        with pytest.raises(ValueError):
            wrapper.encode("xyz")
