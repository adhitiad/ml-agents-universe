"""Economy Dataset: World Bank Indicators (synthetic fallback).

Mengunduh data makroekonomi dari World Bank API atau
men-generate synthetic data yang sesuai dengan schema `macro_indicators.yaml`.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import polars as pl

from shared.data.downloader import DatasetDownloader

logger = logging.getLogger(__name__)

# Indikator World Bank yang umum
_WB_INDICATORS: dict[str, str] = {
    "NY.GDP.MKTP.CD": "GDP_current_USD",
    "FP.CPI.TOTL.ZG": "Inflation_CPI",
    "SL.UEM.TOTL.ZS": "Unemployment_rate",
}

_SAMPLE_COUNTRIES: list[str] = [
    "IDN", "USA", "CHN", "JPN", "DEU", "GBR", "IND", "BRA", "KOR", "SGP",
    "MYS", "THA", "VNM", "PHL", "AUS", "CAN", "FRA", "ITA", "MEX", "RUS",
]


def fetch_world_bank_data(
    indicator: str,
    countries: list[str],
    start_year: int = 2015,
    end_year: int = 2023,
) -> list[dict[str, Any]]:
    """Fetch data dari World Bank API v2.

    Args:
        indicator: Kode indikator World Bank.
        countries: List kode negara ISO3.
        start_year: Tahun awal.
        end_year: Tahun akhir.

    Returns:
        List of dict berisi data indikator.
    """
    records: list[dict[str, Any]] = []
    country_str = ";".join(countries)
    url = (
        f"https://api.worldbank.org/v2/country/{country_str}"
        f"/indicator/{indicator}"
        f"?date={start_year}:{end_year}&format=json&per_page=1000"
    )

    try:
        resp = httpx.get(url, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()

        if len(data) < 2 or data[1] is None:
            logger.warning("Tidak ada data dari World Bank untuk %s", indicator)
            return records

        indicator_name = _WB_INDICATORS.get(indicator, indicator)
        for entry in data[1]:
            if entry.get("value") is not None:
                records.append(
                    {
                        "country": entry["country"]["id"],
                        "indicator": indicator_name,
                        "value": float(entry["value"]),
                        "timestamp": datetime(
                            int(entry["date"]), 1, 1, tzinfo=timezone.utc
                        ),
                    }
                )
    except Exception as e:
        logger.warning("World Bank API error untuk %s: %s", indicator, e)

    return records


def generate_synthetic_economy_data(n_records: int = 500) -> list[dict[str, Any]]:
    """Generate synthetic macro-economy data.

    Args:
        n_records: Jumlah record yang di-generate.

    Returns:
        List of dict sesuai schema macro_indicators.yaml.
    """
    records: list[dict[str, Any]] = []
    indicators = ["GDP_current_USD", "Inflation_CPI", "Unemployment_rate"]

    value_ranges: dict[str, tuple[float, float]] = {
        "GDP_current_USD": (1e9, 2e13),
        "Inflation_CPI": (0.5, 15.0),
        "Unemployment_rate": (1.0, 25.0),
    }

    for i in range(n_records):
        country = random.choice(_SAMPLE_COUNTRIES)  # noqa: S311
        indicator = random.choice(indicators)  # noqa: S311
        low, high = value_ranges[indicator]
        value = round(random.uniform(low, high), 4)  # noqa: S311
        year = random.randint(2015, 2023)  # noqa: S311

        records.append(
            {
                "country": country,
                "indicator": indicator,
                "value": value,
                "timestamp": datetime(year, 1, 1, tzinfo=timezone.utc),
            }
        )
    return records


def download_economy_dataset(
    *,
    use_api: bool = True,
    n_fallback: int = 500,
    output_dir: Path | None = None,
) -> Path:
    """Download atau generate Economy dataset.

    Args:
        use_api: Jika True, coba fetch dari World Bank API.
        n_fallback: Jumlah record untuk synthetic fallback.
        output_dir: Direktori output. Default: data/raw/economy/.

    Returns:
        Path ke file parquet output.
    """
    downloader = DatasetDownloader()
    dest_dir = output_dir or downloader.domain_dir("economy")
    output_path = dest_dir / "world_bank_indicators.parquet"

    if output_path.exists():
        logger.info("Dataset Economy sudah ada: %s", output_path)
        return output_path

    all_records: list[dict[str, Any]] = []

    if use_api:
        logger.info("Fetching data dari World Bank API...")
        for indicator_code in _WB_INDICATORS:
            records = fetch_world_bank_data(indicator_code, _SAMPLE_COUNTRIES)
            all_records.extend(records)
            logger.info(
                "  %s: %d records",
                _WB_INDICATORS[indicator_code],
                len(records),
            )

    if not all_records:
        logger.warning("API data kosong, fallback ke synthetic data.")
        all_records = generate_synthetic_economy_data(n_fallback)

    df = pl.DataFrame(all_records)
    df.write_parquet(output_path)
    logger.info("Economy dataset tersimpan: %s (%d baris)", output_path, df.height)
    return output_path
