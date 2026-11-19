import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sequence():
    return "ATCG"


class TestSante:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestEndpointEncode:
    def test_encode_one2one(self, client):
        response = client.get("/tests/encode", params={"data": "0101", "strategy": "one2one"})
        assert response.status_code == 200
        body = response.json()
        assert body["input"] == "0101"
        assert len(body["encoded"]) == 4
        assert all(base in "ATCG" for base in body["encoded"])
        assert body["encoder"] == "one2one"

    def test_encode_strategie_inconnue(self, client):
        response = client.get("/tests/encode", params={"data": "01", "strategy": "inconnu"})
        assert response.status_code == 400

    def test_encode_entree_invalide(self, client):
        response = client.get("/tests/encode", params={"data": "ADN", "strategy": "one2one"})
        assert response.status_code == 400


class TestEndpointDecode:
    def test_decode_one2one(self, client, sequence):
        response = client.get("/tests/decode", params={"sequence": sequence, "strategy": "one2one"})
        assert response.status_code == 200
        body = response.json()
        assert body["decoded"] == "0011"
        assert body["decoder"] == "one2one"

    def test_decode_strategie_inconnue(self, client):
        response = client.get("/tests/decode", params={"sequence": "ATCG", "strategy": "inconnu"})
        assert response.status_code == 400


class TestEndpointCanal:
    def test_canal_sans_erreur(self, client, sequence):
        response = client.get(
            "/tests/channel",
            params={"sequence": sequence, "error_rate": 0.0, "strategy": "substitution"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["transmitted"] == sequence
        assert body["errors"] == []

    def test_canal_avec_graine(self, client):
        params = {"sequence": "ATCG" * 10, "error_rate": 0.3, "seed": 42, "strategy": "substitution"}
        body1 = client.get("/tests/channel", params=params).json()
        body2 = client.get("/tests/channel", params=params).json()
        assert body1["transmitted"] == body2["transmitted"]

    def test_canal_strategie_inconnue(self, client):
        response = client.get("/tests/channel", params={"sequence": "ATCG", "strategy": "bruit"})
        assert response.status_code == 400

    def test_canal_taux_invalide(self, client):
        response = client.get("/tests/channel", params={"sequence": "ATCG", "error_rate": 2.0})
        assert response.status_code == 400


class TestEndpointProtection:
    def test_protection(self, client, sequence):
        response = client.get("/tests/protection", params={"sequence": sequence, "mode": "protect"})
        assert response.status_code == 200
        assert response.json()["output"] == "AAATTTCCCGGG"

    def test_restauration(self, client):
        response = client.get(
            "/tests/protection",
            params={"sequence": "AATCCC", "mode": "restore"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["output"] == "AC"
        assert body["corrections"][0]["corrected"] == "A"

    def test_mode_inconnu(self, client, sequence):
        response = client.get("/tests/protection", params={"sequence": sequence, "mode": "bruit"})
        assert response.status_code == 400

    def test_strategie_inconnue(self, client, sequence):
        response = client.get("/tests/protection", params={"sequence": sequence, "strategy": "hamming"})
        assert response.status_code == 400


class TestCommunicationComplete:
    def run_(self, client, **overrides):
        payload = {
            "message": "Test CI",
            "error_rate": 0.0,
            "use_protection": True,
        }
        payload.update(overrides)
        return client.post("/communication/run", json=payload)

    def test_chaine_sans_protection_sans_erreur(self, client):
        response = self.run_(client, use_protection=False)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["integrity"] is True
        assert body["received_message"] == body["original_message"]

    def test_canal_modele1_recoit_ses_parametres(self, client):
        response = self.run_(
            client,
            channel="modele1",
            use_protection=False,
            pts=0.0,
            pi=0.0,
            pd=0.0,
        )
        assert response.status_code == 200
        body = response.json()
        channel_step = next(step for step in body["steps"] if step["id"] == "channel")
        assert channel_step["errors"] == []
        assert body["integrity"] is True

    def test_canal_modele1_avec_indels_ne_bloque_pas_la_chaine(self, client):
        response = self.run_(
            client,
            channel="modele1",
            use_protection=True,
            pts=0.0,
            pi=0.1,
            pd=0.1,
            seed=7,
        )
        assert response.status_code == 200
        body = response.json()
        step_ids = [step["id"] for step in body["steps"]]
        assert "restore" in step_ids
        assert "result" in step_ids

    def test_chaine_avec_protection_bas_taux(self, client):
        response = self.run_(client, error_rate=0.05, seed=1234)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["integrity"] is True
        assert body["stats"]["protection"] is True

    def test_etapes_completes_dans_l_ordre(self, client):
        body = self.run_(client, use_protection=True).json()
        ids = [step["id"] for step in body["steps"]]
        assert ids == [
            "source",
            "bits",
            "encode",
            "protect",
            "channel",
            "restore",
            "decode",
            "result",
        ]

    def test_etapes_sans_protection(self, client):
        body = self.run_(client, use_protection=False).json()
        ids = [step["id"] for step in body["steps"]]
        assert "protect" not in ids
        assert "restore" not in ids

    def test_structure_des_etapes(self, client):
        body = self.run_(client, use_protection=True).json()
        for step in body["steps"]:
            assert set(step.keys()) >= {
                "id",
                "label",
                "description",
                "kind",
                "input_kind",
                "output_kind",
                "input",
                "output",
            }

    def test_reproductibilite_avec_graine(self, client):
        body1 = self.run_(client, error_rate=0.25, seed=777).json()
        body2 = self.run_(client, error_rate=0.25, seed=777).json()
        channel1 = next(s for s in body1["steps"] if s["id"] == "channel")
        channel2 = next(s for s in body2["steps"] if s["id"] == "channel")
        # Toutes les étapes aléatoires (encodeur, canal) dépendent de la graine
        assert channel1["output"] == channel2["output"]
        assert body1["stats"]["errors_injected"] == body2["stats"]["errors_injected"]

    def test_message_vide_refuse(self, client):
        response = self.run_(client, message="")
        assert response.status_code == 422

    def test_message_avec_caracteres_speciaux(self, client):
        response = self.run_(client, message="Héllo, wörld! 42 ✓")
        assert response.status_code == 200
        assert response.json()["integrity"] is True
