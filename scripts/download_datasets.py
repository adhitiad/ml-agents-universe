"""CLI untuk mengunduh dan mempersiapkan dataset semua domain agent.

Usage:
    python scripts/download_datasets.py                    # Download semua (versi kecil)
    python scripts/download_datasets.py --domain nlp finance  # Domain tertentu saja
    python scripts/download_datasets.py --full             # Download versi lengkap
    python scripts/download_datasets.py --clean            # Hapus data lama, download ulang
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path


# Menambahkan root direktori ke sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import polars as pl


# Force UTF-8 output di Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("download_datasets")

# Registry domain → download function
_DOMAIN_REGISTRY: dict[str, dict[str, str]] = {
    "nlp": {
        "module": "agents.nlp.src.data.dataset",
        "function": "download_nlp_dataset",
        "description": "WhatsApp Intent Classification",
    },
    "finance": {
        "module": "agents.finance.src.data.dataset",
        "function": "download_finance_dataset",
        "description": "Bitcoin Hourly OHLCV",
    },
    "economy": {
        "module": "agents.economy.src.data.dataset",
        "function": "download_economy_dataset",
        "description": "World Bank Macro Indicators",
    },
    "education": {
        "module": "agents.education.src.data.dataset",
        "function": "download_education_dataset",
        "description": "ASSISTments-style Knowledge Tracing",
    },
    "entertainment": {
        "module": "agents.entertainment.src.data.dataset",
        "function": "download_entertainment_dataset",
        "description": "MovieLens Ratings",
    },
    "mathematics": {
        "module": "agents.mathematics.src.data.dataset",
        "function": "download_mathematics_dataset",
        "description": "DeepTheorem Theorem-Proof Pairs",
    },
    "science": {
        "module": "agents.science.src.data.dataset",
        "function": "download_science_dataset",
        "description": "QM9 Molecular Properties",
    },
    "healthcare": {
        "module": "agents.healthcare.src.data.dataset",
        "function": "download_healthcare_dataset",
        "description": "Healthcare Dummy Dataset",
    },
    "legal": {
        "module": "agents.legal.src.data.dataset",
        "function": "download_legal_dataset",
        "description": "Legal Dummy Dataset",
    },
    "cybersecurity": {
        "module": "agents.cybersecurity.src.data.dataset",
        "function": "download_cybersecurity_dataset",
        "description": "Cybersecurity Dummy Dataset",
    },
    "creative": {
        "module": "agents.creative.src.data.dataset",
        "function": "download_creative_dataset",
        "description": "Creative Dummy Dataset",
    },
    "devops": {
        "module": "agents.devops.src.data.dataset",
        "function": "download_devops_dataset",
        "description": "DevOps Dummy Dataset",
    },
    "data_engineering": {
        "module": "agents.data_engineering.src.data.dataset",
        "function": "download_data_engineering_dataset",
        "description": "Data Eng Dummy Dataset",
    },
    "osint": {
        "module": "agents.osint.src.data.dataset",
        "function": "download_osint_dataset",
        "description": "OSINT Dummy Dataset",
    },
    "game_ai": {
        "module": "agents.game_ai.src.data.dataset",
        "function": "download_game_ai_dataset",
        "description": "Game AI Dummy Dataset",
    },
    "productivity": {
        "module": "agents.productivity.src.data.dataset",
        "function": "download_productivity_dataset",
        "description": "Productivity Dummy Dataset",
    },
}

_ALL_DOMAINS = list(_DOMAIN_REGISTRY.keys())


def download_domain(domain: str, *, full: bool = False) -> dict[str, str | int | float]:
    """Download dataset untuk satu domain.

    Args:
        domain: Nama domain agent.
        full: Jika True, download versi lengkap.

    Returns:
        Dict berisi hasil download.
    """
    import importlib

    info = _DOMAIN_REGISTRY[domain]
    module = importlib.import_module(info["module"])
    download_func = getattr(module, info["function"])

    start = time.time()

    # Tentukan parameter berdasarkan mode
    kwargs: dict[str, int | bool] = {}
    if full:
        # Versi lengkap: lebih banyak data
        if domain == "nlp":
            kwargs = {"n_samples": 5000, "use_huggingface": True}
        elif domain == "finance":
            kwargs = {"n_hours": 8760}  # 1 tahun
        elif domain == "economy":
            kwargs = {"use_api": True}
        elif domain == "education":
            kwargs = {"n_students": 200, "n_interactions": 50}
        elif domain == "entertainment":
            kwargs = {"use_movielens": True}
        elif domain == "mathematics":
            kwargs = {"n_samples": 5000, "use_huggingface": True}
        elif domain == "science":
            kwargs = {"n_samples": 5000}

    output_path = download_func(**kwargs)
    elapsed = time.time() - start

    # Baca file untuk statistik
    df = pl.read_parquet(output_path)
    file_size = output_path.stat().st_size

    return {
        "domain": domain,
        "description": info["description"],
        "status": "OK",
        "rows": df.height,
        "columns": df.width,
        "file_size_kb": round(file_size / 1024, 1),
        "time_sec": round(elapsed, 2),
        "path": str(output_path),
    }


def print_results_table(results: list[dict[str, str | int | float]]) -> None:
    """Cetak tabel ringkasan hasil download.

    Args:
        results: List of dict hasil download per domain.
    """
    # Header
    print("\n" + "=" * 100)
    print(f"{'Domain':<15} {'Dataset':<35} {'Status':<8} {'Rows':>8} {'Size':>10} {'Time':>8}")
    print("-" * 100)

    total_rows = 0
    total_size = 0.0

    for r in results:
        rows = r.get("rows", 0)
        size = r.get("file_size_kb", 0.0)
        total_rows += int(rows)
        total_size += float(size)

        print(
            f"{r['domain']:<15} "
            f"{r['description']!s:<35} "
            f"{r['status']:<8} "
            f"{rows:>8} "
            f"{size:>8.1f}KB "
            f"{r.get('time_sec', 0):>6.2f}s"
        )

    print("-" * 100)
    print(f"{'TOTAL':<15} {'':<35} {'':8} {total_rows:>8} {total_size:>8.1f}KB")
    print("=" * 100)


def main() -> None:
    """Entry point CLI."""
    parser = argparse.ArgumentParser(
        description="Download dan persiapkan dataset untuk ML Agents Universe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python scripts/download_datasets.py                       # Semua domain, versi kecil
  python scripts/download_datasets.py --domain nlp finance   # Domain tertentu
  python scripts/download_datasets.py --full                 # Versi lengkap
  python scripts/download_datasets.py --clean                # Hapus lama, download ulang
        """,
    )

    parser.add_argument(
        "--domain",
        nargs="+",
        choices=_ALL_DOMAINS,
        default=_ALL_DOMAINS,
        help="Domain yang akan didownload (default: semua).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Download versi lengkap dataset (lebih besar, lebih lambat).",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Hapus data existing sebelum download ulang.",
    )

    args = parser.parse_args()

    print("\n🚀 ML Agents Universe — Dataset Downloader")
    print(f"   Mode: {'FULL' if args.full else 'SMALL (default)'}")
    print(f"   Domains: {', '.join(args.domain)}")
    print()

    # Clean jika diminta
    if args.clean:
        data_raw = Path(__file__).resolve().parents[1] / "data" / "raw"
        for domain in args.domain:
            domain_dir = data_raw / domain
            if domain_dir.exists():
                logger.info("Menghapus data lama: %s", domain_dir)
                for f in domain_dir.glob("*.parquet"):
                    f.unlink()

    # Download per domain
    results: list[dict[str, str | int | float]] = []
    for domain in args.domain:
        print(f"📦 Memproses {domain}...")
        try:
            result = download_domain(domain, full=args.full)
            results.append(result)
        except Exception as e:
            logger.error("Gagal memproses %s: %s", domain, e)
            results.append(
                {
                    "domain": domain,
                    "description": _DOMAIN_REGISTRY[domain]["description"],
                    "status": "FAIL",
                    "rows": 0,
                    "file_size_kb": 0,
                    "time_sec": 0,
                    "path": "",
                }
            )

    # Tampilkan ringkasan
    print_results_table(results)

    # Ringkasan akhir
    ok_count = sum(1 for r in results if r["status"] == "OK")
    fail_count = len(results) - ok_count
    print(f"\n✅ {ok_count} domain berhasil", end="")
    if fail_count > 0:
        print(f" | ❌ {fail_count} domain gagal", end="")
    print("\n")


if __name__ == "__main__":
    main()
