"""Memori jangka pendek (RAM) Multi-Tenant berbasis Cache Global.

Menyimpan history pesan langsung di memori RAM server. Dirancang khusus
dengan sistem Cache Global (Dictionary) sehingga instance memori dapat
dibentuk secara aman pada sistem stateless seperti webhook FastAPI.
"""

from __future__ import annotations

import logging

from langchain_core.messages import BaseMessage


logger = logging.getLogger(__name__)

# Penyimpanan RAM global di tingkat modul yang hidup selama proses Python aktif
_GLOBAL_RAM_BUFFER: dict[str, list[BaseMessage]] = {}


class ShortTermMemory:
    """Memori berbasis buffer FIFO (First In First Out) untuk konteks seketika.

    Dioptimasi untuk sistem Multi-Tenant (Omnichannel) sehingga histori
    Telegram User A dan Discord User B tidak akan bertabrakan.
    """

    def __init__(self, session_id: str, max_messages: int = 50) -> None:
        """Inisialisasi memori jangka pendek untuk sesi tertentu.

        Args:
            session_id: ID unik pengguna atau grup obrolan (contoh: user_123).
            max_messages: Batas jumlah pesan maksimum sebelum pesan terlama (FIFO) dihapus
                          untuk menjaga kapasitas RAM dan batas konteks LLM.
        """
        self.session_id = session_id
        self.max_messages = max_messages

        # Inisialisasi slot untuk sesi ini jika belum ada di RAM
        if self.session_id not in _GLOBAL_RAM_BUFFER:
            _GLOBAL_RAM_BUFFER[self.session_id] = []
            logger.debug(
                f"Mengalokasikan ShortTermMemory baru di RAM untuk sesi: {self.session_id}"
            )

    @property
    def _messages(self) -> list[BaseMessage]:
        """Akses instan ke cache global sesuai session_id."""
        return _GLOBAL_RAM_BUFFER[self.session_id]

    def add_message(self, message: BaseMessage) -> None:
        """Tambahkan pesan ke buffer. Hapus yang tertua jika melebihi batas pesan (FIFO)."""
        buffer = self._messages
        buffer.append(message)

        if len(buffer) > self.max_messages:
            # Membuang pesan tertua (index 0)
            buffer.pop(0)

    def get_messages(self, limit: int | None = None) -> list[BaseMessage]:
        """Ambil salinan (list) pesan dari memori.

        Args:
            limit: Jumlah maksimum pesan terbaru yang diambil.
        """
        buffer = self._messages
        if limit is None:
            return list(buffer)
        return list(buffer[-limit:])

    def clear(self) -> None:
        """Bersihkan buffer khusus untuk sesi ini."""
        self._messages.clear()
        logger.info(f"ShortTermMemory (RAM) dibersihkan untuk sesi: {self.session_id}")

    def persist(self, path: str = "") -> None:
        """Metode diabaikan. Sesuai desain, memori RAM bersifat volatil dan akan
        hilang jika server API direstart.
        """
        logger.debug("persist() diabaikan pada ShortTermMemory (dirancang volatil).")
        pass

    def load(self, path: str = "") -> None:
        """Metode diabaikan. Tidak ada pemuatan dari file."""
        logger.debug("load() diabaikan pada ShortTermMemory.")
        pass
