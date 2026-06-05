"""Script untuk memverifikasi fungsionalitas Phase 3: Data Pipeline & Lake.
"""

import asyncio
import logging
import sys
from pathlib import Path


# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Import spesifik dari generator agent finance
from agents.finance.src.data.ingestion import extract_data
from shared.data.pipeline import DataPipeline
from shared.data.quality import DataQuality
from shared.data.schema import SchemaRegistry, SchemaValidator
from shared.data.versioning import DataVersioning


async def main():
    print("=" * 50)
    print("=== VERIFIKASI PHASE 3: DATA PIPELINE & LAKE ===")
    print("=" * 50)

    base_dir = Path("e:/dev/ml-agents-universe")

    # 1. Load Schema Registry
    registry = SchemaRegistry(base_dir / "data" / "schemas")
    registry.load_all()

    schema = registry.get("market_data")
    if not schema:
        print("  [ERROR] Skema 'market_data' tidak ditemukan.")
        sys.exit(1)
    print("  [OK] SchemaRegistry dan YAML Parsing berjalan")

    # 2. Inisialisasi dependensi Pipeline
    validator = SchemaValidator(registry)
    quality = DataQuality(max_staleness_hours=24.0)
    versioning = DataVersioning(base_dir / "data" / "processed")
    pipeline = DataPipeline(schema_validator=validator, data_quality=quality, versioning=versioning)

    # 3. Jalankan Pipeline
    print("  [*] Menjalankan pipeline ETL...")
    result = await pipeline.run(
        domain="finance",
        schema=schema,
        extract_generator=extract_data(),
        source_name="verify_script"
    )

    if result.success:
        print("  [OK] DataPipeline ETL berhasil dieksekusi")
        print(f"       Records diproses: {result.records_processed}")
        print(f"       Quality Score: {result.quality_score:.3f}")
        print(f"       Snapshot ID: {result.snapshot_id}")
    else:
        print(f"  [ERROR] Pipeline gagal: {result.error_message}")
        sys.exit(1)

    # 4. Verifikasi Rollback (Versioning)
    try:
        df_restored = versioning.rollback("finance", "market_data", result.snapshot_id)
        if df_restored.height == result.records_processed:
            print("  [OK] DataVersioning rollback dan Parquet I/O berjalan")
        else:
            print("  [ERROR] Jumlah baris rollback tidak sesuai")
            sys.exit(1)
    except Exception as e:
        print(f"  [ERROR] Rollback gagal: {e}")
        sys.exit(1)

    print("=" * 50)
    print("=== SEMUA VERIFIKASI PHASE 3 BERHASIL! ===")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
