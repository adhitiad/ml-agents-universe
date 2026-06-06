"""Schema Validator.

Module ini berfungsi untuk meload skema YAML dari direktori data/schemas/
dan melakukan validasi Polars DataFrame terhadap schema tersebut, atau
melakukan Pydantic-based validation.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import polars as pl
import yaml
from pydantic import BaseModel, Field, ValidationError

from shared.models.base import ColumnType, DataSchema


logger = logging.getLogger(__name__)


# Mapping dari ColumnType ke Polars dtype families untuk validasi DataFrame
_TYPE_MAP: dict[ColumnType, set[type]] = {
    ColumnType.STRING: {pl.Utf8, pl.String},
    ColumnType.INTEGER: {pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64},
    ColumnType.FLOAT: {pl.Float32, pl.Float64},
    ColumnType.BOOLEAN: {pl.Boolean},
    ColumnType.DATETIME: {pl.Datetime, pl.Date, pl.Time},
}


class SchemaRegistry:
    """Registry untuk menampung loaded schemas dan versi."""

    def __init__(self, schemas_dir: Path | str) -> None:
        self.schemas_dir = Path(schemas_dir)
        self.schemas: dict[str, DataSchema] = {}

    def load_all(self) -> None:
        """Load semua file .yaml di schemas_dir secara rekursif."""
        if not self.schemas_dir.exists():
            logger.warning("Directory schemas tidak ditemukan: %s", self.schemas_dir)
            return

        for yaml_path in self.schemas_dir.rglob("*.yaml"):
            try:
                self.load_schema(yaml_path)
            except Exception as e:
                logger.error("Gagal meload schema dari %s: %s", yaml_path, str(e))

    def load_schema(self, path: Path) -> DataSchema:
        """Parse yaml ke DataSchema Pydantic object."""
        with path.open("r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)

        try:
            schema = DataSchema(**raw_data)
            self.schemas[schema.name] = schema
            logger.info("Berhasil meload schema '%s' (v%s)", schema.name, schema.version)
            return schema
        except ValidationError as e:
            logger.error("Schema '%s' tidak valid secara struktur Pydantic: %s", path.name, str(e))
            raise

    def get(self, name: str) -> DataSchema | None:
        """Dapatkan schema berdasarkan nama."""
        return self.schemas.get(name)


class SchemaValidator:
    """Validator DataFrame Polars terhadap DataSchema."""

    def __init__(self, registry: SchemaRegistry | None = None) -> None:
        self.registry = registry

    def validate_df(self, df: pl.DataFrame, schema: DataSchema) -> list[str]:
        """Memvalidasi DF dan mengembalikan list error (kosong jika valid)."""
        errors = []
        df_columns = set(df.columns)

        for col_def in schema.columns:
            # 1. Pengecekan Eksistensi Kolom
            if col_def.name not in df_columns:
                if not col_def.nullable:
                    errors.append(f"Missing required column: {col_def.name}")
                continue

            series = df[col_def.name]

            # 2. Pengecekan Null
            if not col_def.nullable:
                null_count = series.null_count()
                if null_count > 0:
                    errors.append(f"Column '{col_def.name}' contains {null_count} nulls but is non-nullable.")

            # 3. Pengecekan Tipe Data
            expected_dtypes = _TYPE_MAP.get(col_def.type)
            if expected_dtypes is not None:
                if type(series.dtype) not in expected_dtypes:
                    errors.append(
                        f"Type mismatch on '{col_def.name}': expected {col_def.type.value}, got {series.dtype}"
                    )

            # 4. Pengecekan Constraints
            self._check_constraints(series, col_def.constraints, col_def.name, errors)

        return errors

    def _check_constraints(self, series: pl.Series, constraints: dict[str, Any], col_name: str, errors: list[str]) -> None:
        if not constraints:
            return

        if "min" in constraints:
            min_val = constraints["min"]
            actual_min = series.drop_nulls().min()
            if actual_min is not None and actual_min < min_val:
                errors.append(f"Column '{col_name}' violated min constraint: {actual_min} < {min_val}")

        if "max" in constraints:
            max_val = constraints["max"]
            actual_max = series.drop_nulls().max()
            if actual_max is not None and actual_max > max_val:
                errors.append(f"Column '{col_name}' violated max constraint: {actual_max} > {max_val}")

        if constraints.get("unique", False):
            if series.n_unique() < series.len():
                errors.append(f"Column '{col_name}' violated unique constraint.")


class NormalizedMessage(BaseModel):
    """Schema standar untuk pesan dari berbagai platform Omnichannel."""
    
    message_id: str = Field(..., description="ID unik pesan dari platform asal")
    platform: str = Field(..., description="Nama platform: telegram, whatsapp, discord, dsb")
    chat_id: str = Field(..., description="ID dari chat atau grup tempat pesan dikirim")
    sender_id: str = Field(..., description="ID unik pengirim pesan")
    content: str = Field(..., description="Teks atau isi pesan yang dikirim")
    timestamp: str = Field(..., description="Waktu pesan dikirim dalam format ISO 8601")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata ekstra (misal: reply_to_id, username, channel_name)")

