import pytest

from app.core.base_channel import BaseCanal
from app.channels.substitution_channel import SubstitutionChannel
from app.wrappers.channel import ChannelWrapper

BASES = "ATCG"


@pytest.fixture
def canal():
    return SubstitutionChannel(error_rate=0.1, seed=42)


@pytest.fixture
def wrapper(canal):
    return ChannelWrapper(canal)


class TestSubstitutionChannel:
    def test_herite_de_la_classe_abstraite(self, canal):
        assert isinstance(canal, BaseCanal)

    def test_taux_zero_ne_modifie_rien(self):
        canal = SubstitutionChannel(error_rate=0.0, seed=1)
        result = canal.transmit("ATCGATCG")
        assert result["output"] == "ATCGATCG"
        assert result["errors"] == []

    def test_taux_cent_pourcent_change_toutes_les_bases(self):
        canal = SubstitutionChannel(error_rate=1.0, seed=1)
        sequence = "ATCG"
        result = canal.transmit(sequence)
        assert result["errors"]
        for error in result["errors"]:
            assert error["received"] != error["original"]
            assert error["received"] in BASES

    def test_longueur_conserved(self, canal):
        result = canal.transmit("ATCG" * 20)
        assert len(result["output"]) == 80

    def test_erreurs_coherentes(self):
        canal = SubstitutionChannel(error_rate=0.2, seed=7)
        result = canal.transmit("ATCGATCGATCG" * 10)
        for error in result["errors"]:
            assert 0 <= error["index"] < 120
            assert error["original"] in BASES
            assert error["received"] in BASES
            assert error["received"] != error["original"]
            assert result["output"][error["index"]] == error["received"]

    def test_reproductibilite_avec_graine(self):
        canal1 = SubstitutionChannel(error_rate=0.3, seed=123)
        canal2 = SubstitutionChannel(error_rate=0.3, seed=123)
        c1 = canal1.transmit("ATCG" * 30)
        c2 = canal2.transmit("ATCG" * 30)
        assert c1["output"] == c2["output"]
        assert c1["errors"] == c2["errors"]

    def test_graines_differentes_differents(self):
        canal1 = SubstitutionChannel(error_rate=0.5, seed=123)
        canal2 = SubstitutionChannel(error_rate=0.5, seed=456)
        c1 = canal1.transmit("ATCG" * 30)
        c2 = canal2.transmit("ATCG" * 30)
        assert c1["output"] != c2["output"] or c1["errors"] != c2["errors"]

    def test_erreur_sur_base_invalide(self, canal):
        with pytest.raises(ValueError):
            canal.transmit("ATCGX")

    def test_erreur_sur_chaine_vide(self, canal):
        result = canal.transmit("")
        assert result["output"] == ""
        assert result["errors"] == []

    def test_taux_erreur_hors_limites(self):
        with pytest.raises(ValueError):
            SubstitutionChannel(error_rate=1.5)
        with pytest.raises(ValueError):
            SubstitutionChannel(error_rate=-0.1)


class TestChannelWrapper:
    def test_delegue_a_la_strategie(self):
        # Deux canaux identiques (même graine) donnent le même résultat
        wrapper = ChannelWrapper(SubstitutionChannel(error_rate=0.1, seed=42))
        canal = SubstitutionChannel(error_rate=0.1, seed=42)
        assert wrapper.transmit("ATCG" * 5) == canal.transmit("ATCG" * 5)

    def test_expose_la_strategie(self, wrapper, canal):
        assert wrapper.strategy is canal

    def test_retourne_un_dict(self, wrapper):
        result = wrapper.transmit("ATCG")
        assert set(result.keys()) == {"output", "errors"}
