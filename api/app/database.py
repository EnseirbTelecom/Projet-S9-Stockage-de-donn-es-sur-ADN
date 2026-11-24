"""Accès à la base de données (stockage des séquences ADN importées).

L'URL de connexion provient de la variable d'environnement `DATABASE_URL`
(docker-compose la renseigne avec PostgreSQL). En développment local sans
Docker, un repli SQLite évite d'installer un serveur de base de données.
"""
import os
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./adn_local.db")

# check_same_thread est requis par SQLite car FastAPI sert les requêtes
# depuis plusieurs threads de travail.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class DnaFile(Base):
    """Fichier importé dont le contenu a été encodé en séquence ADN."""

    __tablename__ = "dna_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    bit_count: Mapped[int] = mapped_column(Integer, nullable=False)
    base_count: Mapped[int] = mapped_column(Integer, nullable=False)
    encoder: Mapped[str] = mapped_column(String(64), nullable=False)
    seed: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sequence: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


def get_db():
    """Dépendance FastAPI : fournit une session et la referme après usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
