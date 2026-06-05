"""ETL Data Pipeline Orchestrator.

Menggabungkan ekstraksi (generik via asyncio generators), validasi skema (schema.py),
penilaian kualitas data (quality.py), dan pemuatan versi (versioning.py).
Mendukung retry mechanism dengan exponential backoff sederhana.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any

import polars as pl
from pydantic import BaseModel

from shared.data.quality import DataQuality
from shared.data.schema import SchemaValidator
from shared.data.versioning import DataVersioning
from shared.models.base import DataSchema


logger = logging.getLogger(__name__)


class PipelineResult(BaseModel):
    success: bool
    domain: str
    schema_name: str
    records_processed: int
    quality_score: float
    error_message: str = ""
    snapshot_id: str = ""


class DataPipeline:
    """Orkestrator proses ETL data secara keseluruhan."""

    def __init__(
        self,
        schema_validator: SchemaValidator,
        data_quality: DataQuality,
        versioning: DataVersioning,
        max_retries: int = 3,
        base_backoff_sec: float = 2.0,
    ) -> None:
        self.schema_validator = schema_validator
        self.data_quality = data_quality
        self.versioning = versioning
        self.max_retries = max_retries
        self.base_backoff_sec = base_backoff_sec

    async def run(
        self,
        domain: str,
        schema: DataSchema,
        extract_generator: AsyncGenerator[dict[str, Any], None],
        transform_func: Callable[[pl.DataFrame], pl.DataFrame] | None = None,
        source_name: str = "pipeline",
    ) -> PipelineResult:
        """Eksekusi pipeline secara end-to-end dengan exponential backoff retry."""
        attempt = 0
        while attempt <= self.max_retries:
            try:
                return await self._execute_run(domain, schema, extract_generator, transform_func, source_name)
            except Exception as e:
                attempt += 1
                if attempt > self.max_retries:
                    logger.error("Pipeline gagal setelah %d percobaan: %s", self.max_retries, str(e))
                    return PipelineResult(
                        success=False,
                        domain=domain,
                        schema_name=schema.name,
                        records_processed=0,
                        quality_score=0.0,
                        error_message=str(e),
                    )
                wait_time = self.base_backoff_sec * (2 ** (attempt - 1))
                logger.warning("Pipeline error: %s. Retrying %d/%d in %.1f seconds...", str(e), attempt, self.max_retries, wait_time)
                await asyncio.sleep(wait_time)

        return PipelineResult(success=False, domain=domain, schema_name=schema.name, records_processed=0, quality_score=0.0, error_message="Unknown failure")

    async def _execute_run(
        self,
        domain: str,
        schema: DataSchema,
        extract_generator: AsyncGenerator[dict[str, Any], None],
        transform_func: Callable[[pl.DataFrame], pl.DataFrame] | None = None,
        source_name: str = "pipeline",
    ) -> PipelineResult:

        # 1. Extract
        logger.info("Mulai ekstraksi data untuk %s/%s", domain, schema.name)
        records = []
        async for record in extract_generator:
            records.append(record)

        if not records:
            raise ValueError("Extract step mengembalikan 0 records.")

        df = pl.DataFrame(records)

        # 2. Transform (Optional)
        if transform_func:
            logger.info("Menjalankan fungsi transformasi kustom.")
            df = transform_func(df)

        # 3. Validate
        logger.info("Memvalidasi skema DataFrame.")
        validation_errors = self.schema_validator.validate_df(df, schema)
        if validation_errors:
            error_str = "; ".join(validation_errors)
            logger.error("Validasi gagal: %s", error_str)
            raise ValueError(f"Validasi Skema Gagal: {error_str}")

        # 4. Data Quality Check
        logger.info("Memeriksa kualitas data.")
        quality_report = self.data_quality.evaluate(df, schema)

        if not quality_report.is_acceptable:
            err = f"Quality score {quality_report.overall_score:.2f} di bawah threshold 0.8."
            logger.error(err)
            raise ValueError(err)

        # 5. Load / Versioning (simpan ke processed)
        logger.info("Membuat snapshot (Versioning).")
        snapshot = self.versioning.create_snapshot(
            df=df,
            domain=domain,
            schema_name=schema.name,
            quality_score=quality_report.overall_score,
            source=source_name,
        )

        logger.info("Pipeline %s/%s sukses! Snapshot: %s", domain, schema.name, snapshot.snapshot_id)
        return PipelineResult(
            success=True,
            domain=domain,
            schema_name=schema.name,
            records_processed=df.height,
            quality_score=quality_report.overall_score,
            snapshot_id=snapshot.snapshot_id,
        )
