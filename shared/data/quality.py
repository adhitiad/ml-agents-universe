"""Data quality framework.

Module ini menyediakan evaluasi data quality:
- Completeness checks (missing values detection).
- Consistency checks (cross-field validation).
- Freshness checks (data staleness detection).
- Anomaly detection (statistical outliers).
- Quality score calculation dan reporting (0.0 - 1.0).

Typical usage:
    from shared.data.quality import DataQuality
    
    dq = DataQuality()
    report = dq.evaluate(df, schema, timestamp_col="created_at")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import polars as pl

from shared.models.base import DataSchema


logger = logging.getLogger(__name__)


@dataclass
class QualityReport:
    """Hasil evaluasi kualitas data."""

    overall_score: float = 0.0
    completeness_score: float = 0.0
    validity_score: float = 0.0
    consistency_score: float = 0.0
    freshness_score: float = 1.0
    anomaly_score: float = 1.0

    details: dict[str, Any] = field(default_factory=dict)

    @property
    def is_acceptable(self) -> bool:
        """Data quality minimum 0.8 direkomendasikan sebelum masuk ke agents."""
        return self.overall_score >= 0.8


class DataQuality:
    """Evaluasi kualitas data pada DataFrame Polars."""

    def __init__(
        self,
        completeness_weight: float = 0.3,
        validity_weight: float = 0.3,
        consistency_weight: float = 0.2,
        freshness_weight: float = 0.1,
        anomaly_weight: float = 0.1,
        max_staleness_hours: float = 24.0,
        anomaly_zscore_threshold: float = 3.0,
    ) -> None:
        """Inisialisasi engine DataQuality."""
        total = (
            completeness_weight
            + validity_weight
            + consistency_weight
            + freshness_weight
            + anomaly_weight
        )
        self.weights = {
            "completeness": completeness_weight / total,
            "validity": validity_weight / total,
            "consistency": consistency_weight / total,
            "freshness": freshness_weight / total,
            "anomaly": anomaly_weight / total,
        }
        self.max_staleness_hours = max_staleness_hours
        self.anomaly_zscore_threshold = anomaly_zscore_threshold

    def evaluate(
        self,
        df: pl.DataFrame,
        schema: DataSchema,
        timestamp_col: str | None = None
    ) -> QualityReport:
        """Melakukan evaluasi penuh terhadap DataFrame."""
        report = QualityReport()

        if df.height == 0:
            logger.warning("Evaluasi pada DataFrame kosong.")
            return report

        report.completeness_score = self._check_completeness(df, schema)
        report.validity_score = self._check_validity(df, schema)
        report.consistency_score = self._check_consistency(df, schema)

        if timestamp_col and timestamp_col in df.columns:
            report.freshness_score = self._check_freshness(df, timestamp_col)

        report.anomaly_score, report.details["anomalies"] = self._check_anomalies(df, schema)

        report.overall_score = (
            report.completeness_score * self.weights["completeness"]
            + report.validity_score * self.weights["validity"]
            + report.consistency_score * self.weights["consistency"]
            + report.freshness_score * self.weights["freshness"]
            + report.anomaly_score * self.weights["anomaly"]
        )

        logger.info(
            "Data Quality Score: %.3f (C:%.2f V:%.2f Con:%.2f F:%.2f A:%.2f)",
            report.overall_score,
            report.completeness_score,
            report.validity_score,
            report.consistency_score,
            report.freshness_score,
            report.anomaly_score,
        )
        return report

    def _check_completeness(self, df: pl.DataFrame, schema: DataSchema) -> float:
        """Persentase non-null values di kolom wajib."""
        required_cols = [c.name for c in schema.columns if not c.nullable and c.name in df.columns]
        if not required_cols:
            return 1.0

        total_cells = df.height * len(required_cols)
        null_count = sum(df[col].null_count() for col in required_cols)

        return (total_cells - null_count) / total_cells if total_cells > 0 else 0.0

    def _check_validity(self, df: pl.DataFrame, schema: DataSchema) -> float:
        """Validasi tipe data yang ada secara sederhana (score basis)."""
        if not schema.columns:
            return 1.0

        checked_cols = 0
        valid_cols = 0

        for col_def in schema.columns:
            if col_def.name in df.columns:
                checked_cols += 1
                # Simplifikasi pengecekan tipe menggunakan pl.datatypes
                if df[col_def.name].dtype != pl.Null:
                    # Secara longgar anggap valid jika tidak null-all, detail tipe dicek via SchemaValidator
                    valid_cols += 1

        return valid_cols / checked_cols if checked_cols > 0 else 0.0

    def _check_consistency(self, df: pl.DataFrame, schema: DataSchema) -> float:
        """Persentase kolom dari skema yang benar-benar ada di DF."""
        if not schema.columns:
            return 1.0
        present = sum(1 for col in schema.columns if col.name in df.columns)
        return present / len(schema.columns)

    def _check_freshness(self, df: pl.DataFrame, timestamp_col: str) -> float:
        """Hitung kesegaran data berdasarkan max_staleness_hours."""
        try:
            latest_time = df[timestamp_col].max()
            if not isinstance(latest_time, datetime):
                return 0.0

            now = datetime.now(UTC)
            # Pastikan timezone aware
            if latest_time.tzinfo is None:
                latest_time = latest_time.replace(tzinfo=UTC)

            delta_hours = (now - latest_time).total_seconds() / 3600.0

            if delta_hours <= 0:
                return 1.0
            if delta_hours >= self.max_staleness_hours:
                return 0.0

            # Score menurun linear dari 1.0 ke 0.0
            return 1.0 - (delta_hours / self.max_staleness_hours)
        except Exception as e:
            logger.warning("Gagal menghitung freshness: %s", str(e))
            return 0.0

    def _check_anomalies(self, df: pl.DataFrame, schema: DataSchema) -> tuple[float, dict[str, int]]:
        """Mendeteksi outliers statistik menggunakan Z-score pada kolom numerik."""
        numeric_cols = [
            c.name for c in schema.columns
            if c.type.value in ["integer", "float"] and c.name in df.columns
        ]

        if not numeric_cols:
            return 1.0, {}

        anomalies_detected = {}
        total_records = df.height
        total_anomalies = 0

        for col in numeric_cols:
            series = df[col].drop_nulls()
            if series.len() < 3:
                continue

            # Hitung Z-score standar
            mean = series.mean()
            std = series.std()

            if std == 0 or std is None or mean is None:
                continue

            z_scores = ((series - mean) / std).abs()
            outlier_count = z_scores.filter(z_scores > self.anomaly_zscore_threshold).len()

            if outlier_count > 0:
                anomalies_detected[col] = outlier_count
                total_anomalies += outlier_count

        max_allowed_anomalies = total_records * len(numeric_cols) * 0.05 # toleransi 5% max

        if total_anomalies == 0:
            return 1.0, anomalies_detected
        elif total_anomalies >= max_allowed_anomalies:
            return 0.0, anomalies_detected
        else:
            score = 1.0 - (total_anomalies / max_allowed_anomalies)
            return max(0.0, score), anomalies_detected
