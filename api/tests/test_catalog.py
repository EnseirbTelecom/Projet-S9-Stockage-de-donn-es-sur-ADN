import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.catalog import REGISTRY, get_strategy, build_strategy


@pytest.fixture
def client():
    return TestClient(app)


EXPECTED_CATEGORIES = ("encoder", "decoder", "channel", "protection")

REQUIRED_KEYS = {"category", "slug", "name", "description", "parameters"}


class TestEndpointCatalog:
    def test_catalogue_disponible(self, client):
        response = client.get("/catalog")
        assert response.status_code == 200

    def test_toutes_les_categories_sont_presents(self, client):
        body = client.get("/catalog").json()
        for category in EXPECTED_CATEGORIES:
            assert category in body, f"Catégorie manquante : {category}"

    def test_chaque_impl_implementation_est_decrite(self, client):
        body = client.get("/catalog").json()
        for category in EXPECTED_CATEGORIES:
            assert len(body[category]) == len(REGISTRY[category])
            for entry in body[category]:
                assert REQUIRED_KEYS <= set(entry.keys()), entry
                assert entry["category"] == category
                assert entry["slug"]
                assert entry["name"]
                assert entry["description"]

    def test_les_slugs_sont_uniques_par_categorie(self, client):
        body = client.get("/catalog").json()
        for category, entries in body.items():
            slugs = [entry["slug"] for entry in entries]
            assert len(slugs) == len(set(slugs))

    def test_parametres_decris(self, client):
        body = client.get("/catalog").json()
        substitution = next(e for e in body["channel"] if e["slug"] == "substitution")
        assert substitution["parameters"]["error_rate"]["type"] == "number"
        assert substitution["parameters"]["error_rate"]["default"] == 0.05
        replication = next(e for e in body["protection"] if e["slug"] == "replication")
        assert replication["parameters"]["factor"]["default"] == 3


class TestRegistre:
    def test_get_strategy_inconnue_leve_valueerror(self):
        with pytest.raises(ValueError):
            get_strategy("encoder", "inexistant")
        with pytest.raises(ValueError):
            get_strategy("categorie", "abracadabra")

    def test_get_strategy_retourne_la_classe(self):
        cls = get_strategy("channel", "substitution")
        from app.channels.substitution_channel import SubstitutionChannel
        assert cls is SubstitutionChannel

    def test_toutes_les_classes_impl_elements_heritent_leur_abc(self):
        from app.core.base_encoder import BaseEncodeur
        from app.core.base_decoder import BaseDecodeur
        from app.core.base_channel import BaseCanal
        from app.core.base_protection import BaseProtection

        assert isinstance(get_strategy("encoder", "one2one")(), BaseEncodeur)
        assert isinstance(get_strategy("decoder", "one2one")(), BaseDecodeur)
        assert isinstance(get_strategy("channel", "substitution")(), BaseCanal)
        assert isinstance(get_strategy("protection", "replication")(), BaseProtection)

    def test_build_strategy_ne_passe_que_les_parametres_acceptes(self):
        # error_rate n'existe pas chez l'encodeur : ne doit pas planter
        encoder = build_strategy("encoder", "one2one", seed=7, error_rate=0.4)
        assert encoder.seed == 7

    def test_build_strategy_passe_les_parametres_concernes(self):
        canal = build_strategy("channel", "substitution", error_rate=0.2, seed=9)
        assert canal.error_rate == 0.2
        assert canal.seed == 9

    def test_build_strategy_inconnue_leve_valueerror(self):
        with pytest.raises(ValueError):
            build_strategy("channel", "bruit")


class TestCommunicationAvecCatalogue:
    def run_(self, client, **overrides):
        payload = {"message": "Catalogue", "error_rate": 0.0, "use_protection": True}
        payload.update(overrides)
        return client.post("/communication/run", json=payload)

    def test_strategies_par_defaut_conservent_integrite(self, client):
        body = self.run_(client).json()
        assert body["integrity"] is True
        assert body["steps"][2]["strategy"] == "one2one"
        assert body["steps"][4]["strategy"] == "substitution"

    def test_les_metas_alimentent_les_etapes(self, client):
        body = self.run_(client).json()
        encode_step = next(s for s in body["steps"] if s["id"] == "encode")
        catalog = client.get("/catalog").json()
        encoder_entry = next(
            e for e in catalog["encoder"] if e["slug"] == encode_step["strategy"]
        )
        assert encode_step["description"] == encoder_entry["description"]

    def test_strategies_inconnues_rejettees(self, client):
        response = self.run_(client, encoder="bidon")
        assert response.status_code == 400
        response = self.run_(client, use_protection=True, protection="bidon")
        assert response.status_code == 400
