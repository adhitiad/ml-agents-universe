import os
from pathlib import Path
import polars as pl

def download_healthcare_dataset(**kwargs) -> Path:
    """Download dummy dataset for healthcare."""
    data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "raw", "healthcare")))
    data_dir.mkdir(parents=True, exist_ok=True)

    output_path = data_dir / "dummy_data.parquet"

    if not output_path.exists() or kwargs.get("force", False):
        # Create dummy data
        df = pl.DataFrame({
            "id": range(1, 101),
            "feature": [f"healthcare_feat_{i}" for i in range(1, 101)],
            "label": [i % 5 for i in range(1, 101)]
        })
        df.write_parquet(output_path)

    return output_path
