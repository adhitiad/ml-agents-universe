"""Mathematics Dataset: DeepTheorem-style Theorem-Proof Pairs.

Men-generate dataset teorema dan bukti matematika
yang sesuai dengan schema `theorem_db.yaml`.
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

# Template teorema per domain matematika
_THEOREM_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "algebra": [
        {
            "statement": "Untuk setiap bilangan real a dan b, (a+b)² = a² + 2ab + b²",
            "domain": "algebra",
        },
        {
            "statement": "Jika ax² + bx + c = 0, maka x = (-b ± √(b²-4ac)) / 2a",
            "domain": "algebra",
        },
        {
            "statement": "Untuk matriks A dan B, det(AB) = det(A) · det(B)",
            "domain": "algebra",
        },
        {
            "statement": "Setiap grup siklik berorde n isomorfik dengan Z/nZ",
            "domain": "algebra",
        },
        {
            "statement": "Ring polinomial F[x] atas field F adalah principal ideal domain",
            "domain": "algebra",
        },
    ],
    "analysis": [
        {
            "statement": "Jika f kontinu pada [a,b], maka f terintegralkan Riemann pada [a,b]",
            "domain": "analysis",
        },
        {
            "statement": "Barisan Cauchy di ruang metrik lengkap selalu konvergen",
            "domain": "analysis",
        },
        {
            "statement": "Deret Taylor: eˣ = Σ(n=0,∞) xⁿ/n! untuk semua x ∈ ℝ",
            "domain": "analysis",
        },
        {
            "statement": "Teorema Nilai Antara: Jika f kontinu dan f(a)<k<f(b), maka ∃c∈(a,b) f(c)=k",
            "domain": "analysis",
        },
        {
            "statement": "Fungsi kontinu pada kompak selalu terbatas dan mencapai supremum",
            "domain": "analysis",
        },
    ],
    "number_theory": [
        {
            "statement": "Terdapat tak berhingga banyak bilangan prima (Euclid)",
            "domain": "number_theory",
        },
        {
            "statement": "Teorema Kecil Fermat: aᵖ ≡ a (mod p) untuk p prima",
            "domain": "number_theory",
        },
        {
            "statement": "Setiap bilangan bulat > 1 memiliki faktorisasi prima yang unik",
            "domain": "number_theory",
        },
        {
            "statement": "Fungsi Euler φ(n) menghitung bilangan yang koprima dengan n",
            "domain": "number_theory",
        },
        {
            "statement": "Kongruensi Kuadratik: x² ≡ a (mod p) solvable iff a^((p-1)/2) ≡ 1 (mod p)",
            "domain": "number_theory",
        },
    ],
    "geometry": [
        {
            "statement": "Pada segitiga siku-siku, a² + b² = c² (Pythagoras)",
            "domain": "geometry",
        },
        {
            "statement": "Jumlah sudut dalam segitiga = 180° (geometri Euklides)",
            "domain": "geometry",
        },
        {
            "statement": "Luas lingkaran = π·r² dan keliling = 2·π·r",
            "domain": "geometry",
        },
        {
            "statement": "Volume bola = (4/3)·π·r³ dan luas permukaan = 4·π·r²",
            "domain": "geometry",
        },
        {
            "statement": "Teorema Desargues berlaku di ruang proyektif dimensi ≥ 3",
            "domain": "geometry",
        },
    ],
    "combinatorics": [
        {
            "statement": "C(n,k) = n! / (k!(n-k)!) untuk 0 ≤ k ≤ n",
            "domain": "combinatorics",
        },
        {
            "statement": "Prinsip Inklusi-Eksklusi: |A∪B| = |A| + |B| - |A∩B|",
            "domain": "combinatorics",
        },
        {
            "statement": "Bilangan Catalan Cₙ = C(2n,n)/(n+1) menghitung triangulasi poligon",
            "domain": "combinatorics",
        },
        {
            "statement": "Teorema Ramsey: R(3,3) = 6 (minimum graf lengkap untuk mono-clique)",
            "domain": "combinatorics",
        },
        {
            "statement": "Derangement: D(n) = n! · Σ(k=0,n) (-1)ᵏ/k!",
            "domain": "combinatorics",
        },
    ],
}


def generate_synthetic_math_data(n_samples: int = 500) -> list[dict[str, Any]]:
    """Generate synthetic theorem database.

    Args:
        n_samples: Jumlah teorema yang di-generate.

    Returns:
        List of dict sesuai schema theorem_db.yaml.
    """
    all_theorems: list[dict[str, str]] = []
    for domain_theorems in _THEOREM_TEMPLATES.values():
        all_theorems.extend(domain_theorems)

    records: list[dict[str, Any]] = []
    for i in range(n_samples):
        template = random.choice(all_theorems)  # noqa: S311
        # Tambahkan variasi
        variation = f" [Variant #{i + 1}]"

        records.append(
            {
                "theorem_id": f"THM_{uuid.uuid4().hex[:8].upper()}",
                "statement": template["statement"] + variation,
                "proven": random.random() > 0.1,  # 90% proven  # noqa: S311
                "timestamp": datetime.now(timezone.utc),
            }
        )
    return records


def download_mathematics_dataset(
    *,
    n_samples: int = 500,
    use_huggingface: bool = False,
    output_dir: Path | None = None,
) -> Path:
    """Download atau generate Mathematics dataset.

    Args:
        n_samples: Jumlah sampel untuk synthetic data.
        use_huggingface: Jika True, coba download DeepTheorem.
        output_dir: Direktori output. Default: data/raw/mathematics/.

    Returns:
        Path ke file parquet output.
    """
    downloader = DatasetDownloader()
    dest_dir = output_dir or downloader.domain_dir("mathematics")
    output_path = dest_dir / "deep_theorem.parquet"

    if output_path.exists():
        logger.info("Dataset Mathematics sudah ada: %s", output_path)
        return output_path

    if use_huggingface:
        try:
            raw_records = downloader.download_huggingface(
                "Jiahao004/DeepTheorem",
                dest_dir / ".hf_cache",
                split="train",
                max_samples=n_samples,
            )
            converted = [
                {
                    "theorem_id": f"DT_{uuid.uuid4().hex[:8].upper()}",
                    "statement": str(r.get("theorem", r.get("statement", ""))),
                    "proven": True,
                    "timestamp": datetime.now(timezone.utc),
                }
                for r in raw_records
            ]
        except Exception:
            logger.warning("HuggingFace download gagal, fallback ke synthetic.")
            converted = generate_synthetic_math_data(n_samples)
    else:
        converted = generate_synthetic_math_data(n_samples)

    df = pl.DataFrame(converted)
    df.write_parquet(output_path)
    logger.info("Mathematics dataset tersimpan: %s (%d baris)", output_path, df.height)
    return output_path
