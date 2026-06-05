"""Memori ekstraksi ringkasan (Summary Memory).

Berguna saat buffer mencapai kapasitas maksimum. Pesan lama diringkas
menjadi satu pesan "System" yang mengandung inti percakapan sebelumnya.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from langchain_core.messages import BaseMessage, SystemMessage


logger = logging.getLogger(__name__)


class SummaryMemory:
    """Mengkompresi pesan lama menggunakan LLM."""

    def __init__(self, summarizer_func: Callable[[list[BaseMessage]], str]) -> None:
        """Args:
        summarizer_func: Fungsi (biasanya membungkus panggilan LLM)
                         yang mengambil daftar pesan dan mengembalikan string ringkasan.
        """
        self.summary: str = ""
        self.summarizer_func = summarizer_func

    def summarize_and_store(self, messages: list[BaseMessage]) -> None:
        """Membuat ringkasan dari sekumpulan pesan dan menggabungkannya dengan ringkasan lama."""
        if not messages:
            return

        try:
            new_summary = self.summarizer_func(messages)
            if self.summary:
                # Jika sudah ada, gabungkan ringkasan lama dan baru.
                # (Secara ideal, kita akan memanggil LLM lagi untuk menggabungkan dua string ini,
                # tapi ini adalah penyederhanaan).
                self.summary = f"{self.summary}\nLalu: {new_summary}"
            else:
                self.summary = new_summary

            logger.debug("Summary memory di-update.")
        except Exception as e:
            logger.error("Gagal melakukan summarization: %s", str(e))

    def get_summary_message(self) -> BaseMessage | None:
        """Kembalikan ringkasan sebagai SystemMessage agar bisa di-inject ke prompt LLM."""
        if not self.summary:
            return None
        return SystemMessage(content=f"Ringkasan obrolan sebelumnya: {self.summary}")

    def clear(self) -> None:
        """Hapus ringkasan."""
        self.summary = ""

    def get_summary_text(self) -> str:
        return self.summary
