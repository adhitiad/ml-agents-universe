"""Entertainment Dataset: MovieLens ml-latest-small.

Mengunduh dataset MovieLens dari GroupLens dan
mengkonversinya ke schema `user_behavior.yaml`.
"""

from __future__ import annotations

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

from shared.data.downloader import DatasetDownloader

logger = logging.getLogger(__name__)

_MOVIELENS_URL = (
    "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
)


def parse_movielens_ratings(ratings_csv: Path) -> list[dict[str, Any]]:
    """Parse file ratings.csv MovieLens ke schema user_behavior.

    Args:
        ratings_csv: Path ke file ratings.csv.

    Returns:
        List of dict sesuai schema user_behavior.yaml.
    """
    records: list[dict[str, Any]] = []

    with open(ratings_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Konversi rating (0.5-5.0) ke durasi simulasi (detik)
            # Rating tinggi = menonton lebih lama
            rating = float(row["rating"])
            duration_sec = int(rating * 30)  # 0.5 → 15s, 5.0 → 150s

            timestamp = datetime.fromtimestamp(
                int(row["timestamp"]), tz=timezone.utc
            )

            records.append(
                {
                    "user_id": str(row["userId"]),
                    "content_id": str(row["movieId"]),
                    "duration_sec": duration_sec,
                    "timestamp": timestamp,
                }
            )

    return records


def generate_synthetic_entertainment_data(
    n_records: int = 500,
) -> list[dict[str, Any]]:
    """Fallback: generate synthetic entertainment data.

    Args:
        n_records: Jumlah record.

    Returns:
        List of dict sesuai schema user_behavior.yaml.
    """
    import random
    from datetime import timedelta

    records: list[dict[str, Any]] = []
    base_time = datetime.now(timezone.utc) - timedelta(days=365)

    for i in range(n_records):
        records.append(
            {
                "user_id": str(random.randint(1, 100)),  # noqa: S311
                "content_id": str(random.randint(1, 500)),  # noqa: S311
                "duration_sec": random.randint(15, 180),  # noqa: S311
                "timestamp": base_time
                + timedelta(
                    days=random.randint(0, 365),  # noqa: S311
                    hours=random.randint(0, 23),  # noqa: S311
                ),
            }
        )
    return records


def download_entertainment_dataset(
    *,
    use_movielens: bool = True,
    n_fallback: int = 500,
    output_dir: Path | None = None,
) -> Path:
    """Download atau generate Entertainment dataset.

    Args:
        use_movielens: Jika True, download MovieLens ml-latest-small.
        n_fallback: Jumlah record untuk synthetic fallback.
        output_dir: Direktori output. Default: data/raw/entertainment/.

    Returns:
        Path ke file parquet output.
    """
    downloader = DatasetDownloader()
    dest_dir = output_dir or downloader.domain_dir("entertainment")
    output_path = dest_dir / "movielens_ratings.parquet"

    if output_path.exists():
        logger.info("Dataset Entertainment sudah ada: %s", output_path)
        return output_path

    records: list[dict[str, Any]] = []

    if use_movielens:
        try:
            extract_dir = dest_dir / "ml-latest-small"
            downloader.download_and_extract_zip(_MOVIELENS_URL, extract_dir)

            # Cari ratings.csv (mungkin di subfolder)
            ratings_files = list(extract_dir.rglob("ratings.csv"))
            if ratings_files:
                logger.info("Parsing MovieLens ratings.csv...")
                records = parse_movielens_ratings(ratings_files[0])
                logger.info("  Parsed %d ratings", len(records))
            else:
                logger.warning("ratings.csv tidak ditemukan dalam ZIP.")
        except Exception as e:
            logger.warning("MovieLens download gagal: %s", e)

    if not records:
        logger.info("Fallback ke synthetic entertainment data.")
        records = generate_synthetic_entertainment_data(n_fallback)

    df = pl.DataFrame(records)
    df.write_parquet(output_path)
    logger.info(
        "Entertainment dataset tersimpan: %s (%d baris)",
        output_path,
        df.height,
    )
    return output_path
