"""Memori jangka panjang berbasis Vector Store (FAISS).

Menyimpan dokumen dan pesan lalu menggunakan teknik semantic search
untuk memanggil kembali informasi yang relevan berdasarkan query.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
except ImportError:
    FAISS = None
    HuggingFaceEmbeddings = None


logger = logging.getLogger(__name__)


class VectorStoreMemory:
    """Long-term memory menggunakan FAISS dan HuggingFace embeddings lokal."""

    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2") -> None:
        if FAISS is None or HuggingFaceEmbeddings is None:
            raise ImportError(
                "FAISS atau HuggingFaceEmbeddings tidak tersedia. "
                "Jalankan: pip install faiss-cpu sentence-transformers"
            )

        logger.info("Menginisialisasi HuggingFaceEmbeddings: %s", embedding_model_name)
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

        # Inisialisasi FAISS kosong dengan fake document pertama
        # FAISS memerlukan setidaknya 1 dokumen untuk di-inisialisasi
        dummy_doc = Document(page_content="[MEMORY_INIT]", metadata={"type": "init"})
        self.vector_store = FAISS.from_documents([dummy_doc], self.embeddings)

    def add_message(self, message: BaseMessage) -> None:
        """Konversi pesan ke Dokumen dan tambahkan ke Vector Store."""
        # Abaikan list/multimedia messages untuk simplicity. Fokus pada string.
        if not isinstance(message.content, str):
            return

        role = (
            "user"
            if isinstance(message, HumanMessage)
            else "agent"
            if isinstance(message, AIMessage)
            else "system"
        )
        text = f"{role.upper()}: {message.content}"
        doc = Document(page_content=text, metadata={"role": role, "is_message": True})
        self.vector_store.add_documents([doc])

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Tambahkan dokumen pengetahuan mentah ke memori."""
        doc = Document(page_content=text, metadata=metadata or {})
        self.vector_store.add_documents([doc])

    def get_messages(self, limit: int | None = None) -> list[BaseMessage]:
        """Tidak relevan untuk vector store mengambil 'N pesan terakhir'.
        Gunakan search_relevant() untuk mengambil berdasarkan konteks.

        Fungsi ini dikembalikan kosong untuk memenuhi protocol.
        """
        logger.warning(
            "VectorStoreMemory.get_messages() tidak seharusnya dipanggil. Gunakan search_relevant()."
        )
        return []

    def search_relevant(self, query: str, k: int = 5) -> list[Document]:
        """Cari dokumen/pesan paling relevan menggunakan semantic search."""
        docs = self.vector_store.similarity_search(query, k=k)
        # Filter out the dummy init document
        return [d for d in docs if d.page_content != "[MEMORY_INIT]"]

    def clear(self) -> None:
        """Reset FAISS indeks."""
        dummy_doc = Document(page_content="[MEMORY_INIT]", metadata={"type": "init"})
        self.vector_store = FAISS.from_documents([dummy_doc], self.embeddings)
        logger.debug("Vector store dibersihkan.")

    def persist(self, path: str) -> None:
        """Simpan indeks FAISS ke direktori."""
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        self.vector_store.save_local(str(dir_path))
        logger.info("Vector store disimpan ke %s", dir_path)

    def load(self, path: str) -> None:
        """Muat indeks FAISS dari direktori."""
        dir_path = Path(path)
        if not dir_path.is_dir() or not (dir_path / "index.faiss").exists():
            logger.warning("Indeks FAISS tidak ditemukan di: %s", dir_path)
            return

        try:
            self.vector_store = FAISS.load_local(
                str(dir_path), self.embeddings, allow_dangerous_deserialization=True
            )
            logger.info("Vector store dimuat dari %s", dir_path)
        except Exception as e:
            logger.error("Gagal memuat vector store: %s", str(e))
            raise
