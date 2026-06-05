"""Protocol dasar untuk sistem memori Agen.

Menyediakan interface `BaseMemory` yang mendefinisikan operasi dasar
yang harus didukung oleh semua jenis memori (short-term maupun long-term).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from langchain_core.messages import BaseMessage


@runtime_checkable
class BaseMemory(Protocol):
    """Protocol standar untuk interaksi memori agen."""

    def add_message(self, message: BaseMessage) -> None:
        """Menyimpan pesan baru ke dalam memori."""
        ...

    def get_messages(self, limit: int | None = None) -> list[BaseMessage]:
        """Mengambil pesan dari memori.

        Args:
            limit: Jumlah maksimum pesan terbaru yang diambil.
        """
        ...

    def clear(self) -> None:
        """Menghapus semua isi memori dari konteks aktif."""
        ...

    def persist(self, path: str) -> None:
        """Menyimpan status memori secara permanen (disk/database)."""
        ...

    def load(self, path: str) -> None:
        """Memuat kembali status memori dari penyimpanan permanen."""
        ...
