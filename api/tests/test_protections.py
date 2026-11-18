import pytest

from app.core.base_protection import BaseProtection
from app.protections.replication_protection import ReplicationProtection
from app.wrappers.protection import ProtectionWrapper


@pytest.fixture
def protection():
    return ReplicationProtection(factor=3)


@pytest.fixture
def wrapper(protection):
    return ProtectionWrapper(protection)


class TestReplicationProtection:
    def test_herite_de_la_classe_abstraite(self, protection):
        assert isinstance(protection, BaseProtection)

    def test_protect_replique_chaque_base(self, protection):
        assert protection.protect("ATCG") == "AAATTTCCCGGG"

    def test_protect_sequence_vide(self, protection):
        assert protection.protect("") == ""

    def test_restore_sans_erreur(self, protection):
        result = protection.restore("AAATTTCCCGGG")
        assert result["output"] == "ATCG"
        assert result["corrections"] == []

    def test_restore_corrige_une_substitution(self, protection):
        # "AC" protege donne AAA CCC ; la 3e base du premier bloc est remplacee
        result = protection.restore("AATCCC")
        assert result["output"] == "AC"
        assert result["corrections"] == [
            {"block": 0, "index": 2, "received": "T", "corrected": "A"}
        ]

    def test_restore_blocs_incoherents_prennent_le_majoritaire(self, protection):
        # Blocs "ATT" et "TTC" : la base majoritaire est T dans les deux cas
        result = protection.restore("ATTTTCGGG")
        assert result["output"] == "TTG"
        assert len(result["corrections"]) == 2


class TestValidation:
    def test_protect_rejete_base_invalide(self, protection):
        with pytest.raises(ValueError):
            protection.protect("ATXG")

    def test_restore_longueur_invalide(self, protection):
        with pytest.raises(ValueError):
            protection.restore("AAAT")  # non multiple du facteur 3

    def test_facteur_invalide(self):
        with pytest.raises(ValueError):
            ReplicationProtection(factor=1)
        with pytest.raises(ValueError):
            ReplicationProtection(factor=2)
        with pytest.raises(ValueError):
            ReplicationProtection(factor=4)

    def test_facteur_valide_5(self):
        protection = ReplicationProtection(factor=5)
        assert protection.protect("AT") == "AAAAATTTTT"


class TestProtectionWrapper:
    def test_delegue_protect(self, wrapper, protection):
        assert wrapper.protect("ATCG") == protection.protect("ATCG")

    def test_delegue_restore(self, wrapper, protection):
        assert wrapper.restore("AAATTT") == protection.restore("AAATTT")

    def test_expose_la_strategie(self, wrapper, protection):
        assert wrapper.strategy is protection
