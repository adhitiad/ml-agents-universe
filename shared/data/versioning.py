"""Data Versioning Framework.

Module ini menyediakan fungsi untuk:
- Pembuatan snapshot (data versioning).
- Pelacakan provenance/lineage.
- Mekanisme rollback ke snapshot tertentu.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import polars as pl
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class SnapshotMetadata(BaseModel):
    """Metadata untuk sebuah data snapshot."""

    snapshot_id: str = Field(..., description="ID unik snapshot (biasanya timestamp string).")
    domain: str = Field(..., description="Domain agen pembuat data.")
    schema_name: str = Field(..., description="Nama skema data.")
    record_count: int = Field(..., description="Jumlah baris dalam dataframe.")
    quality_score: float = Field(..., description="Skor kualitas dari QualityScorer.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: str = Field(default="pipeline", description="Sumber eksekusi ETL.")
    file_path: str = Field(..., description="Path relatif file parquet ke direktori processed.")


class DataVersioning:
    """Manajer versi dan snapshot untuk processed data."""

    def __init__(self, processed_dir: Path | str) -> None:
        self.processed_dir = Path(processed_dir)
        self.metadata_file = self.processed_dir / ".versioning_metadata.json"

        # Load metadata if exists
        self.history: list[dict[str, Any]] = []
        self._load_metadata()

    def _load_metadata(self) -> None:
        if self.metadata_file.exists():
            try:
                with self.metadata_file.open("r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.error("Gagal membaca metadata versioning: %s", str(e))

    def _save_metadata(self) -> None:
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with self.metadata_file.open("w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, default=str)

    def create_snapshot(
        self,
        df: pl.DataFrame,
        domain: str,
        schema_name: str,
        quality_score: float,
        source: str = "pipeline",
    ) -> SnapshotMetadata:
        """Menyimpan dataframe sebagai snapshot di direktori processed."""
        timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"{schema_name}_{timestamp_str}"

        # Path: processed/{domain}/{schema_name}/{snapshot_id}.parquet
        target_dir = self.processed_dir / domain / schema_name
        target_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{snapshot_id}.parquet"
        file_path = target_dir / file_name

        # Simpan DataFrame ke Parquet (fast & compressed)
        df.write_parquet(file_path)
        logger.info("Snapshot disimpan: %s", file_path)

        # Buat metadata
        metadata = SnapshotMetadata(
            snapshot_id=snapshot_id,
            domain=domain,
            schema_name=schema_name,
            record_count=df.height,
            quality_score=quality_score,
            source=source,
            file_path=str(file_path.relative_to(self.processed_dir)),
        )

        self.history.append(metadata.model_dump())
        self._save_metadata()

        return metadata

    def rollback(self, domain: str, schema_name: str, target_snapshot_id: str) -> pl.DataFrame:
        """Memuat sebuah snapshot lama dari history."""
        for entry in reversed(self.history):
            if entry["domain"] == domain and entry["schema_name"] == schema_name and entry["snapshot_id"] == target_snapshot_id:
                file_path = self.processed_dir / entry["file_path"]
                if file_path.exists():
                    logger.info("Rollback berhasil ke snapshot %s", target_snapshot_id)
                    return pl.read_parquet(file_path)
                else:
                    raise FileNotFoundError(f"File untuk snapshot {target_snapshot_id} tidak ditemukan: {file_path}")

        raise ValueError(f"Snapshot {target_snapshot_id} tidak ditemukan di history.")
