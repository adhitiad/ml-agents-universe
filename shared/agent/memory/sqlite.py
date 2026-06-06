"""Memori persisten berbasis SQLite (SQLAlchemy).

Menyimpan history pesan langsung ke database. Memori jenis ini
sangat cocok untuk agen yang butuh memanggil histori obrolan kapan pun
walaupun server API baru saja direstart.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from shared.db.database import SessionLocal
from shared.db.models import ChatMessage


logger = logging.getLogger(__name__)


class SQLiteMemory:
    """Memori berbasis database relasional untuk mempertahankan percakapan secara terus-menerus.

    Patuh pada protocol `BaseMemory`.
    """

    def __init__(self, session_id: str) -> None:
        """Inisialisasi memori untuk session tertentu.

        Args:
            session_id: ID unik pengguna atau grup obrolan (contoh: user_123, chat_999).
        """
        self.session_id = session_id

    def add_message(self, message: BaseMessage) -> None:
        """Simpan pesan ke database SQLite."""
        # Tentukan tipe/role
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "ai"
        elif isinstance(message, SystemMessage):
            role = "system"
        else:
            # Fallback
            role = "unknown"

        content = str(message.content)

        db = SessionLocal()
        try:
            db_message = ChatMessage(
                session_id=self.session_id, role=role, content=content
            )
            db.add(db_message)
            db.commit()
            logger.debug(f"Pesan disimpan ke SQLiteMemory [Session: {self.session_id}]")
        except Exception as e:
            db.rollback()
            logger.error(f"Gagal menyimpan pesan ke SQLite: {e}")
            raise
        finally:
            db.close()

    def get_messages(self, limit: int | None = None) -> list[BaseMessage]:
        """Ambil histori obrolan dari database.

        Args:
            limit: Maksimal baris terakhir yang dikembalikan.
        """
        db = SessionLocal()
        try:
            query = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == self.session_id)
                .order_by(ChatMessage.created_at.desc())
            )

            if limit is not None:
                query = query.limit(limit)

            db_messages = query.all()

            # Balik urutannya agar dari yang paling lama ke paling baru (kronologis)
            db_messages.reverse()

            result: list[BaseMessage] = []
            for m in db_messages:
                role_str = str(m.role)
                if role_str == "user":
                    result.append(HumanMessage(content=str(m.content)))
                elif role_str == "ai":
                    result.append(AIMessage(content=str(m.content)))
                elif role_str == "system":
                    result.append(SystemMessage(content=str(m.content)))
                else:
                    # Generic fallback jika unknown role
                    result.append(HumanMessage(content=str(m.content)))

            return result
        finally:
            db.close()

    def clear(self) -> None:
        """Hapus seluruh histori percakapan milik sesi ini dari database."""
        db = SessionLocal()
        try:
            db.query(ChatMessage).filter(
                ChatMessage.session_id == self.session_id
            ).delete()
            db.commit()
            logger.info(f"Semua histori dihapus untuk sesi {self.session_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Gagal menghapus memori: {e}")
            raise
        finally:
            db.close()

    def persist(self, path: str) -> None:
        """Lewati. SQLiteMemory secara otomatis persistent setiap ada penambahan data."""
        logger.debug(
            "persist() dipanggil di SQLiteMemory, tapi operasi diabaikan (sudah persisten via DB)."
        )
        pass

    def load(self, path: str) -> None:
        """Lewati. SQLiteMemory selalu mengambil data fresh dari database pada saat dipanggil."""
        logger.debug("load() dipanggil di SQLiteMemory, operasi diabaikan.")
        pass
