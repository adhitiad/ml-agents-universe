"""Definisi Model Database (SQLAlchemy)."""

from __future__ import annotations

import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from shared.db.database import Base


class LLMCredential(Base):
    """Tabel untuk menyimpan API Keys provider secara aman.

    Hanya menyimpan data yang terenkripsi. Master key disimpan di .env.
    """

    __tablename__ = "llm_credentials"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String, unique=True, index=True, nullable=False)
    encrypted_key = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<LLMCredential(provider='{self.provider_name}', active={self.is_active})>"
