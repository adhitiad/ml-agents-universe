"""Memori jangka pendek (RAM) Multi-Tenant berbasis Redis & Global Cache.

Menyimpan history pesan langsung di memori Redis server. Jika Redis
mati atau tidak dapat dijangkau, sistem akan otomatis jatuh (fallback)
ke Global Dictionary (RAM lokal) agar aplikasi tidak crash.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from shared.env.settings import DatabaseSettings


logger = logging.getLogger(__name__)

# Penyimpanan RAM global sebagai Fallback jika Redis tidak menyala
_GLOBAL_RAM_BUFFER: dict[str, list[BaseMessage]] = {}

# Koneksi Redis Tunggal
_redis_client = None
_redis_available = False

try:
    import redis

    settings = DatabaseSettings()
    # Ping awal untuk memeriksa apakah server Redis menyala
    _temp_client = redis.from_url(settings.redis_url)
    _temp_client.ping()

    # Jika berhasil, simpan klien yang valid
    _redis_client = _temp_client
    _redis_available = True
    logger.info(
        "Koneksi Redis untuk ShortTermMemory BERHASIL (Cross-worker cache aktif)."
    )
except ImportError:
    logger.warning("Paket 'redis' tidak terinstall. Jatuh ke mode RAM Global.")
except Exception as e:
    logger.warning(
        f"Server Redis tidak dapat dijangkau ({e}). Jatuh ke mode RAM Global."
    )


class ShortTermMemory:
    """Memori berbasis buffer FIFO (First In First Out) menggunakan Redis atau RAM Global.

    Dioptimasi untuk sistem Multi-Tenant (Omnichannel) dengan keunggulan:
    - Cross-worker persistence jika dijalankan melalui uvicorn.
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
        self.redis_key = f"chat_memory:{self.session_id}"

        # Jika menggunakan Fallback (RAM), inisialisasi slot untuk sesi ini
        if not _redis_available and self.session_id not in _GLOBAL_RAM_BUFFER:
            _GLOBAL_RAM_BUFFER[self.session_id] = []

    def add_message(self, message: BaseMessage) -> None:
        """Tambahkan pesan ke buffer. Hapus yang tertua jika melebihi batas pesan (FIFO)."""
        if _redis_available and _redis_client is not None:
            try:
                # Serialisasi objek Langchain ke JSON string
                msg_dict = message_to_dict(message)
                msg_json = json.dumps(msg_dict)

                # Masukkan ke ujung kanan Redis list
                _redis_client.rpush(self.redis_key, msg_json)

                # Potong array untuk mempertahankan batas (ltrim mempertahankan dari index tertentu ke akhir)
                # Contoh: Jika kita ingin menyimpan 50 item terakhir, kita memotong dari -50 ke -1
                _redis_client.ltrim(self.redis_key, -self.max_messages, -1)

                # Tambahkan expiration (opsional) agar memori tidak selamanya ada di Redis
                # (misal 24 jam tidak aktif, memori terhapus)
                _redis_client.expire(self.redis_key, 86400)
                return
            except Exception as e:
                logger.error(f"Gagal menyimpan memori ke Redis: {e}")
                # Melanjutkan ke fallback di bawahnya

        # --- Fallback: Global RAM ---
        buffer = _GLOBAL_RAM_BUFFER[self.session_id]
        buffer.append(message)
        if len(buffer) > self.max_messages:
            buffer.pop(0)

    def get_messages(self, limit: int | None = None) -> list[BaseMessage]:
        """Ambil salinan (list) pesan dari memori.

        Args:
            limit: Jumlah maksimum pesan terbaru yang diambil.
        """
        if _redis_available and _redis_client is not None:
            try:
                start_index = 0 if limit is None else -limit
                # Ambil item dari list
                raw_items = _redis_client.lrange(self.redis_key, start_index, -1)

                # Pylance kadang keliru mendeteksi klien sinkron sebagai async (Awaitable) pada redis v5+
                raw_items_list: list = raw_items  # type: ignore
                # Deserialisasi kembali menjadi objek Langchain
                dict_items = [json.loads(item) for item in raw_items_list]
                return messages_from_dict(dict_items)
            except Exception as e:
                logger.error(f"Gagal mengambil memori dari Redis: {e}")
                return []

        # --- Fallback: Global RAM ---
        buffer = _GLOBAL_RAM_BUFFER[self.session_id]
        if limit is None:
            return list(buffer)
        return list(buffer[-limit:])

    def clear(self) -> None:
        """Bersihkan buffer khusus untuk sesi ini."""
        if _redis_available and _redis_client is not None:
            try:
                _redis_client.delete(self.redis_key)
            except Exception as e:
                logger.error(f"Gagal menghapus memori Redis: {e}")

        # Selalu bersihkan fallback juga jika ada
        if self.session_id in _GLOBAL_RAM_BUFFER:
            _GLOBAL_RAM_BUFFER[self.session_id].clear()

        logger.info(
            f"ShortTermMemory (Redis/RAM) dibersihkan untuk sesi: {self.session_id}"
        )

    def persist(self, path: str = "") -> None:
        """Metode diabaikan. Redis otomatis persisten/tersimpan terpusat."""
        pass

    def load(self, path: str = "") -> None:
        """Metode diabaikan. Get selalu mengambil data mutakhir."""
        pass
