"""Memori jangka panjang berbasis Vector Store (FAISS).

Menyimpan dokumen dan pesan lalu menggunakan teknik semantic search
untuk memanggil kembali informasi yang relevan berdasarkan query.
Didesain Multi-Tenant (Per-Session) agar privasi data pengguna Omnichannel terjaga.
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
    """Long-term memory menggunakan FAISS dan HuggingFace embeddings lokal.
    
    Dioptimasi untuk sistem Multi-Tenant di mana setiap `session_id` memiliki 
    ruang vektor (FAISS index file) yang terisolasi sendiri-sendiri di disk lokal.
    """

    def __init__(self, session_id: str, embedding_model_name: str = "all-MiniLM-L6-v2") -> None:
        """Inisialisasi memori jangka panjang untuk sesi spesifik.
        
        Args:
            session_id: ID sesi pengguna/grup unik (misal: telegram_12345).
            embedding_model_name: Model semantic embeddings (sentence-transformers).
        """
        if FAISS is None or HuggingFaceEmbeddings is None:
            raise ImportError(
                "FAISS atau HuggingFaceEmbeddings tidak tersedia. "
                "Jalankan: pip install faiss-cpu sentence-transformers"
            )

        self.session_id = session_id
        # Setiap sesi punya direktori khusus untuk menjaga privasi absolut (Multi-Tenant)
        self.persist_dir = Path("data/long_term_memory") / self.session_id
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.persist_dir / "index.faiss"

        logger.info(f"Memuat Long-Term Memory (FAISS) untuk Sesi: {self.session_id}")
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

        if self.index_file.exists():
            # Load dari index yang sudah ada
            try:
                self.vector_store = FAISS.load_local(
                    str(self.persist_dir), self.embeddings, allow_dangerous_deserialization=True
                )
                logger.info(f"Berhasil memuat memori yang ada untuk sesi {self.session_id}")
            except Exception as e:
                logger.error(f"Gagal meload FAISS untuk {self.session_id}: {e}")
                self._init_empty_faiss()
        else:
            self._init_empty_faiss()

    def _init_empty_faiss(self):
        """Buat instansi FAISS kosong menggunakan dummy document pertama."""
        if FAISS is None:
            raise RuntimeError("FAISS module is missing")
            
        dummy_doc = Document(page_content="[MEMORY_INIT]", metadata={"type": "init", "session_id": self.session_id})
        self.vector_store = FAISS.from_documents([dummy_doc], self.embeddings)
        self.persist()  # Langsung simpan struktur dasar kosong ini ke disk

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
        
        # Tambahkan ke memori
        doc = Document(
            page_content=text, 
            metadata={"role": role, "is_message": True, "session_id": self.session_id}
        )
        self.vector_store.add_documents([doc])
        
        # Auto-save ke disk
        self.persist()

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> None:
        """Tambahkan dokumen pengetahuan mentah ke memori."""
        meta = metadata or {}
        meta["session_id"] = self.session_id
        doc = Document(page_content=text, metadata=meta)
        self.vector_store.add_documents([doc])
        self.persist()

    def get_messages(self, limit: int | None = None) -> list[BaseMessage]:
        """Tidak relevan untuk vector store mengambil 'N pesan terakhir'.
        Gunakan search_relevant() untuk mengambil berdasarkan konteks.

        Fungsi ini dikembalikan kosong untuk memenuhi protocol `BaseMemory`.
        """
        logger.warning(
            "VectorStoreMemory.get_messages() tidak seharusnya dipanggil. Gunakan search_relevant()."
        )
        return []

    def search_relevant(self, query: str, k: int = 5) -> list[Document]:
        """Cari dokumen/pesan paling relevan dari memori sesi ini menggunakan semantic search."""
        # Secara fisik data sudah dipisah per-folder, jadi hasil pencarian dijamin 100% 
        # hanya milik `session_id` yang sedang aktif ini.
        docs = self.vector_store.similarity_search(query, k=k)
        # Filter out the dummy init document
        return [d for d in docs if d.page_content != "[MEMORY_INIT]"]

    def clear(self) -> None:
        """Reset memori indeks sesi ini dan mulai dari nol."""
        self._init_empty_faiss()
        logger.info(f"Vector store untuk sesi {self.session_id} telah dikosongkan.")

    def persist(self, path: str = "") -> None:
        """Simpan indeks FAISS ke direktori khusus sesi ini.
        Parameter `path` diabaikan karena rute telah ditetapkan otomatis per sesi.
        """
        try:
            self.vector_store.save_local(str(self.persist_dir))
        except Exception as e:
            logger.error(f"Gagal persist memori FAISS: {e}")

    def load(self, path: str = "") -> None:
        """Abaikan parameter `path`. 
        Memori sudah diload otomatis saat __init__ berdasarkan `session_id`.
        """
        pass
