import os
from pathlib import Path
import polars as pl
import logging

logger = logging.getLogger(__name__)

try:
    from datasets import load_dataset
except ImportError:
    raise ImportError("Harap jalankan: pip install datasets pyarrow polars")

def download_cybersecurity_dataset(**kwargs) -> Path:
    """Download HuggingFace dataset untuk domain cybersecurity."""
    # Ambil Token HF dari environment (berguna untuk dataset private/gated)
    hf_token = os.environ.get("HF_TOKEN")

    data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "raw", "cybersecurity")))
    data_dir.mkdir(parents=True, exist_ok=True)

    output_path = data_dir / "cybersecurity_dataset.parquet"

    force_clean = kwargs.get("force", False)
    is_full = kwargs.get("full", False)

    if not output_path.exists() or force_clean:
        logger.info(f"Mengunduh dataset Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset dari HuggingFace...")

        # Mengunduh dataset tanpa trust_remote_code
        ds = load_dataset("Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset", token=hf_token)

        if hasattr(ds, "keys"):
            split_name = "train" if "train" in ds.keys() else list(ds.keys())[0]
            ds = ds[split_name]

        if not is_full and len(ds) > 1000:
            ds = ds.select(range(1000))

        # OPTIMASI: Konversi via PyArrow agar 100% kompatibel dengan Polars DataFrame
        # Menghindari error tipe data kompleks (nested json/list)
        try:
            df = pl.from_arrow(ds.data.table)
            df.write_parquet(str(output_path))
        except Exception as e:
            logger.warning(f"Gagal konversi native arrow. Fallback ke Pandas: {e}")
            df = pl.from_pandas(ds.to_pandas())
            df.write_parquet(str(output_path))

    return output_path
