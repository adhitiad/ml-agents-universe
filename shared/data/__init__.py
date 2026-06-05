"""Data loading, validation, dan transformation utilities.

Module ini menyediakan:
- DataLoader (Protocol): Interface untuk semua data loaders
- CSVLoader, JSONLoader, ParquetLoader: Polars-based loaders
- YAMLConfigLoader: YAML config loader
- DataValidator: Schema validation
- QualityScorer: Data quality scoring (0.0-1.0)
- get_loader_for_file: Auto-detect loader dari file extension
"""

from shared.data.loaders import (
    CSVLoader,
    DataLoader,
    JSONLoader,
    ParquetLoader,
    YAMLConfigLoader,
    get_loader_for_file,
)
from shared.data.pipeline import DataPipeline, PipelineResult
from shared.data.quality import DataQuality, QualityReport
from shared.data.schema import SchemaRegistry, SchemaValidator
from shared.data.versioning import DataVersioning, SnapshotMetadata


__all__: list[str] = [
    "CSVLoader",
    "DataLoader",
    "DataPipeline",
    "DataQuality",
    "DataVersioning",
    "JSONLoader",
    "ParquetLoader",
    "PipelineResult",
    "QualityReport",
    "SchemaRegistry",
    "SchemaValidator",
    "SnapshotMetadata",
    "YAMLConfigLoader",
    "get_loader_for_file",
]
