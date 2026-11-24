"""Tests des endpoints de stockage de fichiers ADN (`/files`)."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # Base SQLite en mémoire partagée entre les connexions de la session.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestImport:
    def test_import_fichier_texte(self, client):
        response = client.post(
            "/files/import",
            files={"file": ("note.txt", b"ADN", "text/plain")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["filename"] == "note.txt"
        assert body["byte_size"] == 3
        assert body["bit_count"] == 24
        assert body["base_count"] == 24
        assert body["encoder"] == "one2one"
        assert len(body["sha256"]) == 64
        assert all(base in "ATCG" for base in body["preview"])

    def test_import_binaire(self, client):
        data = bytes(range(256))
        body = client.post(
            "/files/import", files={"file": ("data.bin", data, "application/octet-stream")}
        ).json()
        assert body["byte_size"] == 256
        assert body["base_count"] == 2048

    def test_import_encodeur_gray(self, client):
        data = b"AB"  # 16 bits -> 8 bases (2 bits par base)
        body = client.post(
            "/files/import",
            params={"encoder": "gray"},
            files={"file": ("g.bin", data, "application/octet-stream")},
        ).json()
        assert body["encoder"] == "gray"
        assert body["bit_count"] == 16
        assert body["base_count"] == 8

    def test_import_graine_reproductible(self, client):
        files = {"file": ("r.txt", b"seed", "text/plain")}
        body1 = client.post("/files/import", params={"seed": 42}, files=files).json()
        body2 = client.post("/files/import", params={"seed": 42}, files=files).json()
        assert body1["preview"] == body2["preview"]
        assert body1["sha256"] == body2["sha256"]

    def test_import_encodeur_inconnu(self, client):
        response = client.post(
            "/files/import",
            params={"encoder": "inconnu"},
            files={"file": ("a.txt", b"abc", "text/plain")},
        )
        assert response.status_code == 400

    def test_import_fichier_vide_refuse(self, client):
        response = client.post(
            "/files/import", files={"file": ("vide.txt", b"", "text/plain")}
        )
        assert response.status_code == 400

    def test_import_fichier_trop_lourd_refuse(self, client):
        response = client.post(
            "/files/import",
            files={"file": ("gros.bin", b"x" * (512 * 1024 + 1), "application/octet-stream")},
        )
        assert response.status_code == 413


class TestListe:
    def test_liste_apres_import(self, client):
        client.post("/files/import", files={"file": ("a.txt", b"aa", "text/plain")})
        client.post("/files/import", files={"file": ("b.txt", b"bb", "text/plain")})
        body = client.get("/files").json()
        assert len(body) == 2
        assert body[0]["filename"] == "b.txt"
        assert "sequence" not in body[0]


class TestTelechargement:
    def test_aller_retour_contenu_original(self, client):
        original = "Contenu à encoder : Héllo ✓ 42"
        body = client.post(
            "/files/import", files={"file": ("doc.txt", original.encode("utf-8"), "text/plain")}
        ).json()

        response = client.get(f"/files/{body['id']}/download")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        assert "attachment" in response.headers["content-disposition"]
        assert response.headers["content-disposition"].endswith('doc.txt.dna.txt"')

        # Le contenu téléchargé, relu depuis la base, redécode vers le fichier original.
        from app.decoders.one2one_decoder import One2OneDecoder

        sequence = response.text
        assert sequence == body["preview"] or len(sequence) == body["base_count"]
        decoded_bits = One2OneDecoder().decode(sequence)
        decoded_bytes = bytes(
            int(decoded_bits[i:i + 8], 2) for i in range(0, len(decoded_bits), 8)
        )
        assert decoded_bytes.decode("utf-8") == original

    def test_telechargement_inconnu(self, client):
        response = client.get("/files/999/download")
        assert response.status_code == 404
