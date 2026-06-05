"""Konfigurasi Database Utama dengan SQLAlchemy."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Path default ke file SQLite di direktori data
_DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "ml_agents.db"
_DEFAULT_DB_URL = f"sqlite:///{_DEFAULT_DB_PATH}"

# Ambil dari env, fallback ke SQLite
DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_DB_URL)

# Pastikan folder data ada jika pakai SQLite default
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: Any = declarative_base()


def get_db():
    """Generator untuk mendapatkan database session.

    Digunakan terutama dengan FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Inisialisasi tabel di database."""
    Base.metadata.create_all(bind=engine)
