-- Schéma de la base PostgreSQL (exécuté au premier démarrage du conteneur).
-- Miroir du modèle SQLAlchemy `app/database.py` (creée aussi automatiquement
-- au démarrage de l'API via Base.metadata.create_all, idempotent).

CREATE TABLE IF NOT EXISTS dna_files (
    id          SERIAL PRIMARY KEY,
    filename    VARCHAR(255) NOT NULL,
    sha256      CHAR(64)     NOT NULL,
    byte_size   INTEGER      NOT NULL,
    bit_count   INTEGER      NOT NULL,
    base_count  INTEGER      NOT NULL,
    encoder     VARCHAR(64)  NOT NULL,
    seed        BIGINT,
    sequence    TEXT         NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);
