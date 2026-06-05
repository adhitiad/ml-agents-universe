"""Education Dataset: Synthetic ASSISTments-style Knowledge Tracing.

Men-generate data interaksi siswa yang realistis
sesuai dengan schema `student_logs.yaml`.
"""

from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import polars as pl

from shared.data.downloader import DatasetDownloader

logger = logging.getLogger(__name__)

# Skill/topic categories
_SKILLS: list[str] = [
    "addition",
    "subtraction",
    "multiplication",
    "division",
    "fractions",
    "decimals",
    "algebra_basic",
    "geometry_area",
    "geometry_perimeter",
    "statistics_mean",
]

# Action types
_ACTIONS: list[str] = [
    "attempt",
    "hint_request",
    "correct_answer",
    "incorrect_answer",
    "skip",
]


def generate_synthetic_education_data(
    n_students: int = 50,
    n_interactions_per_student: int = 20,
) -> list[dict[str, Any]]:
    """Generate synthetic student interaction data (ASSISTments-style).

    Mensimulasikan perilaku siswa yang beragam: ada yang
    mahir (skor tinggi), ada yang masih belajar (banyak hint).

    Args:
        n_students: Jumlah siswa unik.
        n_interactions_per_student: Rata-rata interaksi per siswa.

    Returns:
        List of dict sesuai schema student_logs.yaml.
    """
    records: list[dict[str, Any]] = []
    base_time = datetime.now(timezone.utc) - timedelta(days=30)

    for s in range(n_students):
        student_id = f"STU_{uuid.uuid4().hex[:8].upper()}"
        # Setiap siswa punya "kemampuan" acak
        ability = random.gauss(0.65, 0.15)  # noqa: S311
        ability = max(0.1, min(0.95, ability))

        n_interactions = random.randint(  # noqa: S311
            n_interactions_per_student // 2,
            n_interactions_per_student * 2,
        )

        for i in range(n_interactions):
            # Siswa dengan ability tinggi lebih sering correct
            if random.random() < ability:  # noqa: S311
                action = "correct_answer"
                score = round(random.uniform(70, 100), 1)  # noqa: S311
            elif random.random() < 0.3:  # noqa: S311
                action = "hint_request"
                score = round(random.uniform(30, 60), 1)  # noqa: S311
            else:
                action = random.choice(  # noqa: S311
                    ["incorrect_answer", "attempt", "skip"]
                )
                score = round(random.uniform(0, 50), 1)  # noqa: S311

            timestamp = base_time + timedelta(
                hours=random.randint(0, 720),  # noqa: S311
                minutes=random.randint(0, 59),  # noqa: S311
            )

            records.append(
                {
                    "student_id": student_id,
                    "action": action,
                    "score": score,
                    "timestamp": timestamp,
                }
            )

    return records


def download_education_dataset(
    *,
    n_students: int = 50,
    n_interactions: int = 20,
    output_dir: Path | None = None,
) -> Path:
    """Generate Education dataset.

    Args:
        n_students: Jumlah siswa unik.
        n_interactions: Rata-rata interaksi per siswa.
        output_dir: Direktori output. Default: data/raw/education/.

    Returns:
        Path ke file parquet output.
    """
    downloader = DatasetDownloader()
    dest_dir = output_dir or downloader.domain_dir("education")
    output_path = dest_dir / "student_interactions.parquet"

    if output_path.exists():
        logger.info("Dataset Education sudah ada: %s", output_path)
        return output_path

    logger.info(
        "Generating synthetic education data (%d siswa, ~%d interaksi/siswa)...",
        n_students,
        n_interactions,
    )
    records = generate_synthetic_education_data(n_students, n_interactions)

    df = pl.DataFrame(records)
    df.write_parquet(output_path)
    logger.info("Education dataset tersimpan: %s (%d baris)", output_path, df.height)
    return output_path
