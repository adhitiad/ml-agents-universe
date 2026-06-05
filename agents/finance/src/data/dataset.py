"""Finance Dataset: Bitcoin Hourly OHLCV (synthetic fallback).

Mengunduh atau men-generate data OHLCV yang sesuai
dengan schema `market_data.yaml`.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import polars as pl

from shared.data.downloader import DatasetDownloader

logger = logging.getLogger(__name__)


def generate_synthetic_ohlcv(n_hours: int = 720) -> list[dict[str, Any]]:
    """Generate synthetic Bitcoin OHLCV data (30 hari default).

    Args:
        n_hours: Jumlah jam data yang di-generate.

    Returns:
        List of dict sesuai schema market_data.yaml.
    """
    records: list[dict[str, Any]] = []
    base_price = 65000.0
    base_time = datetime.now(timezone.utc) - timedelta(hours=n_hours)

    for i in range(n_hours):
        # Random walk sederhana untuk harga
        change_pct = random.gauss(0, 0.005)  # noqa: S311
        base_price *= 1 + change_pct
        price = round(base_price, 2)
        volume = round(random.uniform(100, 5000), 2)  # noqa: S311

        records.append(
            {
                "symbol": "BTC/USD",
                "price": price,
                "volume": volume,
                "timestamp": base_time + timedelta(hours=i),
            }
        )
    return records


def download_finance_dataset(
    *,
    n_hours: int = 720,
    output_dir: Path | None = None,
) -> Path:
    """Download atau generate Finance dataset.

    Args:
        n_hours: Jumlah jam untuk synthetic data.
        output_dir: Direktori output. Default: data/raw/finance/.

    Returns:
        Path ke file parquet output.
    """
    downloader = DatasetDownloader()
    dest_dir = output_dir or downloader.domain_dir("finance")
    output_path = dest_dir / "btc_ohlcv.parquet"

    if output_path.exists():
        logger.info("Dataset Finance sudah ada: %s", output_path)
        return output_path

    # Gunakan synthetic data (Kaggle dataset butuh API key)
    logger.info("Generating synthetic BTC/USD OHLCV data (%d jam)...", n_hours)
    records = generate_synthetic_ohlcv(n_hours)

    df = pl.DataFrame(records)
    df.write_parquet(output_path)
    logger.info("Finance dataset tersimpan: %s (%d baris)", output_path, df.height)
    return output_path
