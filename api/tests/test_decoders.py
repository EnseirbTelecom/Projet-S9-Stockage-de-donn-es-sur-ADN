import pytest

from app.core.base_decoder import BaseDecodeur
from app.decoders.one2one_decoder import One2OneDecoder
from app.encoders.one2one_encoder import One2OneEncoder
from app.wrappers.decode import DecodeWrapper


@pytest.fixture
def decoder():
    return One2OneDecoder()


@pytest.fixture
def encoder():
    return One2OneEncoder()


@pytest.fixture
def wrapper(decoder):
    return DecodeWrapper(decoder)


class TestOne2OneDecoder:
    def test_herite_de_la_classe_abstraite(self, decoder):
        assert isinstance(decoder, BaseDecodeur)

    def test_at_devient_zero(self, decoder):
        assert decoder.decode("ATAT") == "0000"

    def test_cg_devient_un(self, decoder):
        assert decoder.decode("CGCG") == "1111"

    def test_sequence_mixte(self, decoder):
        assert decoder.decode("ATCG") == "0011"

    def test_sequence_vide(self, decoder):
        assert decoder.decode("") == ""

    def test_bases_inconnues_ignorees(self, decoder):
        assert decoder.decode("ATAXT") == "0000"


class TestAllerRetour:
    def test_round_trip(self, encoder, decoder):
        assert decoder.decode(encoder.encode("010011")) == "010011"

    def test_round_trip_message_long(self, encoder, decoder):
        bits = "1" * 50 + "0" * 50 + "01011010"
        assert decoder.decode(encoder.encode(bits)) == bits


class TestDecodeWrapper:
    def test_delegue_a_la_strategie(self, wrapper, decoder):
        assert wrapper.decode("ATCG") == decoder.decode("ATCG")

    def test_expose_la_strategie(self, wrapper, decoder):
        assert wrapper.strategy is decoder
