"""NLP Dataset: WhatsApp Intent (synthetic fallback).

Mengunduh atau men-generate dataset intent classification
yang sesuai dengan schema `corpus.yaml`.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

from shared.data.downloader import DatasetDownloader

logger = logging.getLogger(__name__)

# Kategori intent untuk synthetic data
_INTENT_CATEGORIES: list[str] = [
    "greeting",
    "complaint",
    "payment_issue",
    "product_inquiry",
    "farewell",
]

_SYNTHETIC_TEMPLATES: dict[str, list[str]] = {
    "greeting": [
        "Halo, selamat pagi!",
        "Hi, ada yang bisa dibantu?",
        "Assalamualaikum, saya mau tanya.",
        "Selamat siang, saya pelanggan baru.",
        "Hey, apa kabar?",
    ],
    "complaint": [
        "Produk saya rusak, tolong bantu.",
        "Saya sangat kecewa dengan pelayanan ini.",
        "Pengiriman terlambat 3 hari, tidak bisa diterima.",
        "Kualitas barang tidak sesuai deskripsi.",
        "Customer service tidak responsif sama sekali.",
    ],
    "payment_issue": [
        "Pembayaran saya gagal, kenapa ya?",
        "Saldo sudah terpotong tapi pesanan belum masuk.",
        "Bagaimana cara refund?",
        "Metode pembayaran apa saja yang tersedia?",
        "Transfer sudah berhasil tapi status masih pending.",
    ],
    "product_inquiry": [
        "Apakah produk ini tersedia dalam warna merah?",
        "Berapa harga untuk paket premium?",
        "Ada diskon untuk pembelian grosir?",
        "Kapan stok akan tersedia kembali?",
        "Spesifikasi laptop ini apa saja?",
    ],
    "farewell": [
        "Terima kasih banyak atas bantuannya!",
        "Oke, sudah jelas. Sampai jumpa!",
        "Baik, saya akan coba dulu. Bye!",
        "Makasih ya, sangat membantu.",
        "Selesai, terima kasih. Wassalam.",
    ],
}


def generate_synthetic_nlp_data(n_samples: int = 500) -> list[dict[str, Any]]:
    """Generate synthetic intent classification data.

    Args:
        n_samples: Jumlah sampel yang di-generate.

    Returns:
        List of dict sesuai schema corpus.yaml.
    """
    import random

    records: list[dict[str, Any]] = []
    for i in range(n_samples):
        intent = random.choice(_INTENT_CATEGORIES)  # noqa: S311
        text = random.choice(_SYNTHETIC_TEMPLATES[intent])  # noqa: S311
        # Tambahkan variasi kecil
        variation = f" [{intent.upper()}#{i}]"
        records.append(
            {
                "id": str(uuid.uuid4()),
                "text": text + variation,
                "source": f"synthetic_whatsapp_{intent}",
                "timestamp": datetime.now(timezone.utc),
            }
        )
    return records


def download_nlp_dataset(
    *,
    n_samples: int = 500,
    use_huggingface: bool = False,
    output_dir: Path | None = None,
) -> Path:
    """Download atau generate NLP dataset.

    Args:
        n_samples: Jumlah sampel untuk synthetic data.
        use_huggingface: Jika True, coba download dari HuggingFace.
        output_dir: Direktori output. Default: data/raw/nlp/.

    Returns:
        Path ke file parquet output.
    """
    downloader = DatasetDownloader()
    dest_dir = output_dir or downloader.domain_dir("nlp")
    output_path = dest_dir / "whatsapp_intent.parquet"

    if output_path.exists():
        logger.info("Dataset NLP sudah ada: %s", output_path)
        return output_path

    if use_huggingface:
        try:
            records = downloader.download_huggingface(
                "claritylab/utcd",
                dest_dir / ".hf_cache",
                split="train",
                max_samples=n_samples,
            )
            # Konversi ke schema corpus.yaml
            converted = [
                {
                    "id": str(uuid.uuid4()),
                    "text": str(r.get("text", "")),
                    "source": "huggingface_utcd",
                    "timestamp": datetime.now(timezone.utc),
                }
                for r in records
            ]
        except Exception:
            logger.warning("HuggingFace download gagal, fallback ke synthetic.")
            converted = generate_synthetic_nlp_data(n_samples)
    else:
        converted = generate_synthetic_nlp_data(n_samples)

    df = pl.DataFrame(converted)
    df.write_parquet(output_path)
    logger.info("NLP dataset tersimpan: %s (%d baris)", output_path, df.height)
    return output_path
