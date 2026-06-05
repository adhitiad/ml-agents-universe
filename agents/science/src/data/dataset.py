"""Science Dataset: QM9-style Molecular Property Data.

Men-generate atau mengunduh data properti molekul
yang sesuai dengan schema `molecular_data.yaml`.
"""

from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

from shared.data.downloader import DatasetDownloader

logger = logging.getLogger(__name__)

# SMILES representasi molekul organik kecil (subset QM9-like)
_SAMPLE_MOLECULES: list[dict[str, Any]] = [
    {"smiles": "C", "name": "Methane", "weight": 16.04},
    {"smiles": "CC", "name": "Ethane", "weight": 30.07},
    {"smiles": "CCC", "name": "Propane", "weight": 44.10},
    {"smiles": "CCCC", "name": "Butane", "weight": 58.12},
    {"smiles": "C=C", "name": "Ethylene", "weight": 28.05},
    {"smiles": "C#C", "name": "Acetylene", "weight": 26.04},
    {"smiles": "O", "name": "Water", "weight": 18.02},
    {"smiles": "CO", "name": "Methanol", "weight": 32.04},
    {"smiles": "CCO", "name": "Ethanol", "weight": 46.07},
    {"smiles": "CC=O", "name": "Acetaldehyde", "weight": 44.05},
    {"smiles": "CC(=O)O", "name": "Acetic Acid", "weight": 60.05},
    {"smiles": "c1ccccc1", "name": "Benzene", "weight": 78.11},
    {"smiles": "c1ccc(O)cc1", "name": "Phenol", "weight": 94.11},
    {"smiles": "c1ccc(N)cc1", "name": "Aniline", "weight": 93.13},
    {"smiles": "C(=O)O", "name": "Formic Acid", "weight": 46.03},
    {"smiles": "CC(C)C", "name": "Isobutane", "weight": 58.12},
    {"smiles": "CCCCC", "name": "Pentane", "weight": 72.15},
    {"smiles": "CCCCCC", "name": "Hexane", "weight": 86.18},
    {"smiles": "C1CCCCC1", "name": "Cyclohexane", "weight": 84.16},
    {"smiles": "C1CCC1", "name": "Cyclobutane", "weight": 56.11},
    {"smiles": "N", "name": "Ammonia", "weight": 17.03},
    {"smiles": "CN", "name": "Methylamine", "weight": 31.06},
    {"smiles": "CCN", "name": "Ethylamine", "weight": 45.08},
    {"smiles": "O=C=O", "name": "CO2", "weight": 44.01},
    {"smiles": "C(Cl)(Cl)Cl", "name": "Chloroform", "weight": 119.38},
    {"smiles": "CC(=O)C", "name": "Acetone", "weight": 58.08},
    {"smiles": "CCOC(=O)C", "name": "Ethyl Acetate", "weight": 88.11},
    {"smiles": "c1ccncc1", "name": "Pyridine", "weight": 79.10},
    {"smiles": "C1CCOC1", "name": "THF", "weight": 72.11},
    {"smiles": "CC#N", "name": "Acetonitrile", "weight": 41.05},
]


def generate_synthetic_science_data(n_samples: int = 500) -> list[dict[str, Any]]:
    """Generate synthetic molecular property data (QM9-style).

    Args:
        n_samples: Jumlah molekul yang di-generate.

    Returns:
        List of dict sesuai schema molecular_data.yaml.
    """
    records: list[dict[str, Any]] = []
    for i in range(n_samples):
        base_mol = random.choice(_SAMPLE_MOLECULES)  # noqa: S311
        # Variasikan berat molekul sedikit
        weight_variation = random.gauss(0, 0.5)  # noqa: S311

        records.append(
            {
                "molecule_id": f"MOL_{uuid.uuid4().hex[:8].upper()}",
                "smiles": base_mol["smiles"],
                "weight": round(base_mol["weight"] + weight_variation, 4),
                "timestamp": datetime.now(timezone.utc),
            }
        )
    return records


def download_science_dataset(
    *,
    n_samples: int = 500,
    output_dir: Path | None = None,
) -> Path:
    """Download atau generate Science dataset.

    Args:
        n_samples: Jumlah sampel untuk synthetic data.
        output_dir: Direktori output. Default: data/raw/science/.

    Returns:
        Path ke file parquet output.
    """
    downloader = DatasetDownloader()
    dest_dir = output_dir or downloader.domain_dir("science")
    output_path = dest_dir / "qm9_molecules.parquet"

    if output_path.exists():
        logger.info("Dataset Science sudah ada: %s", output_path)
        return output_path

    logger.info("Generating synthetic QM9-style molecular data (%d samples)...", n_samples)
    records = generate_synthetic_science_data(n_samples)

    df = pl.DataFrame(records)
    df.write_parquet(output_path)
    logger.info("Science dataset tersimpan: %s (%d baris)", output_path, df.height)
    return output_path
