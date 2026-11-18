import pytest

from app.channels.substitution_channel import SubstitutionChannel
from app.protections.replication_protection import ReplicationProtection
from app.encoders.one2one_encoder import One2OneEncoder
from app.decoders.one2one_decoder import One2OneDecoder
from app.wrappers.encode import EncodeWrapper
from app.wrappers.decode import DecodeWrapper
from app.wrappers.channel import ChannelWrapper
from app.wrappers.protection import ProtectionWrapper


class RecordingStrategy:
    """Stratégie factice pour vérifier la délégation du wrapper."""

    def __init__(self, value="ok"):
        self.value = value

    def process(self, data):
        self.data = data
        return self.value


class TestWrappersGeneriques:
    """Un wrapper doit déléguer sans retravailler les données."""

    def test_encode_wrapper(self):
        wrapper = EncodeWrapper(One2OneEncoder())
        assert wrapper.encode("01") in {"AC", "AG", "TC", "TG"}

    def test_decode_wrapper(self):
        wrapper = DecodeWrapper(One2OneDecoder())
        assert wrapper.decode("AT") == "00"

    def test_channel_wrapper(self):
        channel = SubstitutionChannel(error_rate=0.0, seed=1)
        wrapper = ChannelWrapper(channel)
        assert wrapper.transmit("ATCG") == {
            "output": "ATCG",
            "errors": [],
        }

    def test_protection_wrapper(self):
        wrapper = ProtectionWrapper(ReplicationProtection(factor=3))
        assert wrapper.protect("AT") == "AAATTT"
        restored = wrapper.restore("AAATTT")
        assert restored == {"output": "AT", "corrections": []}


class TestCompletChaine:
    """L'aller-retour complet, hors API : la chaîne doit être idempotente
    quand le canal ne produit aucune erreur."""

    def test_chaine_sans_erreur(self):
        message = "Projet S9"
        bits = "".join(f"{octet:08b}" for octet in message.encode("utf-8"))

        encoded = EncodeWrapper(One2OneEncoder()).encode(bits)
        protected = ProtectionWrapper(ReplicationProtection(factor=3)).protect(encoded)
        transmitted = ChannelWrapper(
            SubstitutionChannel(error_rate=0.0, seed=99)
        ).transmit(protected)["output"]
        restored = ProtectionWrapper(ReplicationProtection(factor=3)).restore(transmitted)["output"]
        decoded = DecodeWrapper(One2OneDecoder()).decode(restored)

        message_received = bytes(
            int(decoded[i:i + 8], 2) for i in range(0, len(decoded), 8)
        ).decode("utf-8")

        assert message_received == message

    def test_chaine_avec_erreurs_corrigees(self):
        message = "AB"
        bits = "".join(f"{octet:08b}" for octet in message.encode("utf-8"))

        encoded = EncodeWrapper(One2OneEncoder()).encode(bits)
        protected = ProtectionWrapper(ReplicationProtection(factor=3)).protect(encoded)

        # On corrompt indépendamment une base par bloc de 3
        transmitted = list(protected)
        for bloc, base in enumerate("AB"):
            transmitted[bloc * 3] = "G" if base in "AT" else "A"
        restored = ProtectionWrapper(ReplicationProtection(factor=3)).restore(
            "".join(transmitted)
        )

        assert restored["output"] == encoded
        assert len(restored["corrections"]) == 2

    def test_tous_les_elements_heritent_abc(self):
        from app.core.base_encoder import BaseEncodeur
        from app.core.base_decoder import BaseDecodeur
        from app.core.base_channel import BaseCanal
        from app.core.base_protection import BaseProtection

        assert isinstance(One2OneEncoder(), BaseEncodeur)
        assert isinstance(One2OneDecoder(), BaseDecodeur)
        assert isinstance(SubstitutionChannel(), BaseCanal)
        assert isinstance(ReplicationProtection(), BaseProtection)
