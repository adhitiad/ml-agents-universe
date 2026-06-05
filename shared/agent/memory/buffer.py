"""Memori percakapan jangka pendek.

Merekam history pesan dalam RAM (buffer) dengan sliding window opsional
untuk mencegah context window LLM penuh.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict


logger = logging.getLogger(__name__)


class ConversationBufferMemory:
    """Memori berbasis buffer FIFO (First In First Out) untuk konteks langsung.

    Sangat efisien untuk pesan-pesan terakhir (short-term).
    """

    def __init__(
        self, max_tokens_limit: int | None = None, max_messages: int | None = None
    ) -> None:
        self.messages: list[BaseMessage] = []
        self.max_tokens_limit = max_tokens_limit
        self.max_messages = max_messages

    def add_message(self, message: BaseMessage) -> None:
        """Tambahkan pesan ke buffer. Hapus yang tertua jika melebihi batas pesan."""
        self.messages.append(message)

        if self.max_messages and len(self.messages) > self.max_messages:
            # Pop dari depan (paling lama)
            self.messages.pop(0)

    def get_messages(self, limit: int | None = None) -> list[BaseMessage]:
        """Ambil list pesan."""
        if limit is None:
            return list(self.messages)
        return list(self.messages[-limit:])

    def clear(self) -> None:
        """Bersihkan buffer."""
        self.messages.clear()
        logger.debug("Conversation buffer dibersihkan.")

    def persist(self, path: str) -> None:
        """Simpan buffer ke file JSON."""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        dicts = [message_to_dict(m) for m in self.messages]
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(dicts, f, indent=2, ensure_ascii=False)
        logger.info("Memori buffer disimpan ke %s", file_path)

    def load(self, path: str) -> None:
        """Muat buffer dari file JSON."""
        file_path = Path(path)
        if not file_path.is_file():
            logger.warning("File buffer memori tidak ditemukan: %s", file_path)
            return

        try:
            with file_path.open(encoding="utf-8") as f:
                dicts = json.load(f)
            self.messages = messages_from_dict(dicts)
            logger.info("Memori buffer dimuat: %d pesan", len(self.messages))
        except Exception as e:
            logger.error("Gagal memuat memori buffer: %s", str(e))
            raise
