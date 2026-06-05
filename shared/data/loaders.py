"""Data loaders menggunakan Protocol pattern dan Polars.

Module ini menyediakan interface DataLoader (Protocol) dan
implementasi konkret untuk berbagai format data:
- CSVLoader: CSV files via Polars
- JSONLoader: JSON/JSONL files via Polars
- ParquetLoader: Apache Parquet files via Polars
- YAMLConfigLoader: YAML config files → dict

Semua loaders menggunakan Polars sebagai engine utama untuk performa.

Typical usage:
    from shared.data.loaders import CSVLoader

    loader = CSVLoader()
    df = loader.load("data/raw/finance/market_data.csv")
    loader.save(df, "data/processed/finance/cleaned.parquet")
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import polars as pl
import yaml


logger = logging.getLogger(__name__)


# ==========================================
# DataLoader Protocol
# ==========================================


@runtime_checkable
class DataLoader(Protocol):
    """Protocol untuk data loading dari berbagai sumber.

    Semua concrete loaders harus mengimplementasikan interface ini.
    Gunakan Protocol (bukan ABC) untuk structural subtyping.
    """

    def load(self, source: str | Path, **kwargs: Any) -> pl.DataFrame:
        """Load data dari sumber ke Polars DataFrame.

        Args:
            source: Path ke file sumber data.
            **kwargs: Parameter tambahan untuk loader.

        Returns:
            Polars DataFrame berisi data yang di-load.
        """
        ...

    def save(self, df: pl.DataFrame, target: str | Path, **kwargs: Any) -> None:
        """Simpan DataFrame ke file.

        Args:
            df: Polars DataFrame yang akan disimpan.
            target: Path ke file tujuan.
            **kwargs: Parameter tambahan untuk writer.
        """
        ...


# ==========================================
# CSV Loader
# ==========================================


class CSVLoader:
    """Loader untuk CSV files menggunakan Polars.

    Attributes:
        separator: Delimiter kolom (default: ",").
        encoding: Encoding file (default: "utf-8").
        has_header: Apakah file memiliki header row.
        null_values: Daftar string yang dianggap null.
    """

    def __init__(
        self,
        separator: str = ",",
        encoding: str = "utf-8",
        has_header: bool = True,
        null_values: list[str] | None = None,
    ) -> None:
        """Inisialisasi CSVLoader.

        Args:
            separator: Delimiter kolom.
            encoding: Encoding file.
            has_header: Apakah CSV memiliki header.
            null_values: Strings yang dianggap null.
        """
        self.separator = separator
        self.encoding = encoding
        self.has_header = has_header
        self.null_values = null_values or ["", "NA", "N/A", "null", "None"]

    def load(self, source: str | Path, **kwargs: Any) -> pl.DataFrame:
        """Load CSV file ke Polars DataFrame.

        Args:
            source: Path ke CSV file.
            **kwargs: Parameter tambahan untuk pl.read_csv.

        Returns:
            Polars DataFrame.

        Raises:
            FileNotFoundError: Jika file tidak ditemukan.
        """
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(f"CSV file tidak ditemukan: {path}")

        logger.info("Loading CSV: %s", path)
        df = pl.read_csv(
            path,
            separator=self.separator,
            encoding=self.encoding,
            has_header=self.has_header,
            null_values=self.null_values,
            **kwargs,
        )
        logger.info("CSV loaded: %d rows x %d columns", df.height, df.width)
        return df

    def save(self, df: pl.DataFrame, target: str | Path, **kwargs: Any) -> None:
        """Simpan DataFrame ke CSV file.

        Args:
            df: DataFrame yang akan disimpan.
            target: Path ke file tujuan.
            **kwargs: Parameter tambahan untuk df.write_csv.
        """
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.write_csv(path, separator=self.separator, **kwargs)
        logger.info("CSV saved: %s (%d rows)", path, df.height)


# ==========================================
# JSON Loader
# ==========================================


class JSONLoader:
    """Loader untuk JSON dan JSON Lines files.

    Attributes:
        json_lines: Jika True, baca sebagai JSON Lines (satu JSON per baris).
    """

    def __init__(self, json_lines: bool = False) -> None:
        """Inisialisasi JSONLoader.

        Args:
            json_lines: True untuk JSON Lines format.
        """
        self.json_lines = json_lines

    def load(self, source: str | Path, **kwargs: Any) -> pl.DataFrame:
        """Load JSON/JSONL file ke Polars DataFrame.

        Args:
            source: Path ke JSON file.
            **kwargs: Parameter tambahan.

        Returns:
            Polars DataFrame.

        Raises:
            FileNotFoundError: Jika file tidak ditemukan.
        """
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(f"JSON file tidak ditemukan: {path}")

        logger.info("Loading JSON: %s (lines=%s)", path, self.json_lines)

        if self.json_lines:
            df = pl.read_ndjson(path, **kwargs)
        else:
            # Polars read_json mengharapkan JSON array
            with path.open(encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                df = pl.DataFrame(data, **kwargs)
            elif isinstance(data, dict):
                # Wrap single dict dalam list
                df = pl.DataFrame([data], **kwargs)
            else:
                raise TypeError(
                    f"JSON root harus array atau object, got {type(data).__name__}"
                )

        logger.info("JSON loaded: %d rows x %d columns", df.height, df.width)
        return df

    def save(self, df: pl.DataFrame, target: str | Path, **kwargs: Any) -> None:
        """Simpan DataFrame ke JSON file.

        Args:
            df: DataFrame yang akan disimpan.
            target: Path ke file tujuan.
            **kwargs: Parameter tambahan.
        """
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)

        if self.json_lines:
            df.write_ndjson(path, **kwargs)
        else:
            # Write sebagai JSON array
            rows = df.to_dicts()
            with path.open("w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=2, default=str)

        logger.info("JSON saved: %s (%d rows)", path, df.height)


# ==========================================
# Parquet Loader
# ==========================================


class ParquetLoader:
    """Loader untuk Apache Parquet files.

    Parquet adalah format kolumnar yang efisien untuk
    penyimpanan data besar dengan kompresi otomatis.

    Attributes:
        compression: Algoritma kompresi (zstd, snappy, lz4, gzip).
    """

    def __init__(self, compression: str = "zstd") -> None:
        """Inisialisasi ParquetLoader.

        Args:
            compression: Algoritma kompresi untuk write.
        """
        self.compression = compression

    def load(self, source: str | Path, **kwargs: Any) -> pl.DataFrame:
        """Load Parquet file ke Polars DataFrame.

        Args:
            source: Path ke Parquet file.
            **kwargs: Parameter tambahan untuk pl.read_parquet.

        Returns:
            Polars DataFrame.

        Raises:
            FileNotFoundError: Jika file tidak ditemukan.
        """
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(f"Parquet file tidak ditemukan: {path}")

        logger.info("Loading Parquet: %s", path)
        df = pl.read_parquet(path, **kwargs)
        logger.info("Parquet loaded: %d rows x %d columns", df.height, df.width)
        return df

    def save(self, df: pl.DataFrame, target: str | Path, **kwargs: Any) -> None:
        """Simpan DataFrame ke Parquet file.

        Args:
            df: DataFrame yang akan disimpan.
            target: Path ke file tujuan.
            **kwargs: Parameter tambahan.
        """
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.write_parquet(path, compression=self.compression, **kwargs)
        logger.info("Parquet saved: %s (%d rows)", path, df.height)


# ==========================================
# YAML Config Loader
# ==========================================


class YAMLConfigLoader:
    """Loader khusus untuk YAML configuration files.

    Berbeda dari data loaders lain, ini mengembalikan dict
    bukan DataFrame, karena config files bukan tabular data.
    """

    def load(self, source: str | Path, **kwargs: Any) -> dict[str, Any]:
        """Load YAML config file ke dictionary.

        Args:
            source: Path ke YAML file.
            **kwargs: Tidak digunakan, untuk kompatibilitas interface.

        Returns:
            Dictionary berisi konfigurasi.

        Raises:
            FileNotFoundError: Jika file tidak ditemukan.
        """
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(f"YAML file tidak ditemukan: {path}")

        logger.info("Loading YAML config: %s", path)
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            logger.warning("YAML file kosong: %s", path)
            return {}

        logger.info("YAML loaded: %s (%d keys)", path.name, len(data))
        return data

    def save(self, data: dict[str, Any], target: str | Path, **kwargs: Any) -> None:
        """Simpan dictionary ke YAML file.

        Args:
            data: Dictionary yang akan disimpan.
            target: Path ke file tujuan.
            **kwargs: Parameter tambahan untuk yaml.dump.
        """
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                **kwargs,
            )
        logger.info("YAML saved: %s", path)


# ==========================================
# Factory Function
# ==========================================


def get_loader_for_file(path: str | Path) -> CSVLoader | JSONLoader | ParquetLoader:
    """Dapatkan loader yang sesuai berdasarkan ekstensi file.

    Args:
        path: Path ke file data.

    Returns:
        Instance loader yang sesuai.

    Raises:
        ValueError: Jika ekstensi file tidak didukung.
    """
    suffix = Path(path).suffix.lower()
    loaders: dict[str, CSVLoader | JSONLoader | ParquetLoader] = {
        ".csv": CSVLoader(),
        ".tsv": CSVLoader(separator="\t"),
        ".json": JSONLoader(),
        ".jsonl": JSONLoader(json_lines=True),
        ".ndjson": JSONLoader(json_lines=True),
        ".parquet": ParquetLoader(),
        ".pq": ParquetLoader(),
    }

    if suffix not in loaders:
        supported = ", ".join(sorted(loaders.keys()))
        raise ValueError(
            f"Ekstensi '{suffix}' tidak didukung. "
            f"Format yang didukung: {supported}"
        )

    return loaders[suffix]
