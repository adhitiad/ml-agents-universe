"""CLI untuk mengunduh dan mempersiapkan dataset semua domain agent."""

from __future__ import annotations

import argparse
import importlib
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import polars as pl


# Menambahkan root direktori ke sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure") and sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("download_datasets")

# OPTIMASI: Auto-discovery. Membaca domain langsung dari struktur folder
AGENTS_DIR = Path(__file__).resolve().parents[1] / "agents"
_ALL_DOMAINS = [
    d.name
    for d in AGENTS_DIR.iterdir()
    if d.is_dir() and (d / "src" / "data" / "dataset.py").exists()
]


def download_domain(
    domain: str, full: bool, force: bool
) -> dict[str, str | int | float]:
    """Download dataset secara dinamis menggunakan importlib."""
    module_path = f"agents.{domain}.src.data.dataset"
    func_name = f"download_{domain}_dataset"

    try:
        module = importlib.import_module(module_path)
        download_func = getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Gagal memuat modul untuk {domain}: {e}")
        raise

    start = time.time()

    # Teruskan parameter full dan force (clean) ke masing-masing agen
    kwargs = {"full": full, "force": force}

    output_path = download_func(**kwargs)
    elapsed = time.time() - start

    # Baca statistik via Polars
    df = pl.read_parquet(output_path)
    file_size = output_path.stat().st_size

    return {
        "domain": domain,
        "status": "OK",
        "rows": df.height,
        "columns": df.width,
        "file_size_kb": round(file_size / 1024, 1),
        "time_sec": round(elapsed, 2),
        "path": str(output_path),
    }


def print_results_table(results: list[dict[str, str | int | float]]) -> None:
    print("\n" + "=" * 90)
    print(
        f"{'Domain':<20} {'Status':<10} {'Rows':>10} {'Columns':>10} {'Size':>12} {'Time':>10}"
    )
    print("-" * 90)

    total_rows = 0
    total_size = 0.0

    for r in results:
        rows = r.get("rows", 0)
        size = r.get("file_size_kb", 0.0)
        total_rows += int(rows)
        total_size += float(size)

        status_emoji = "✅ OK" if r["status"] == "OK" else "❌ FAIL"

        print(
            f"{r['domain']:<20} "
            f"{status_emoji:<10} "
            f"{rows:>10} "
            f"{r.get('columns', 0):>10} "
            f"{size:>10.1f} KB "
            f"{r.get('time_sec', 0):>8.2f} s"
        )

    print("-" * 90)
    print(f"{'TOTAL':<20} {'':<10} {total_rows:>10} {'':>10} {total_size:>10.1f} KB")
    print("=" * 90)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download dataset ML Agents secara Paralel."
    )
    parser.add_argument(
        "--domain", nargs="+", choices=_ALL_DOMAINS, default=_ALL_DOMAINS
    )
    parser.add_argument("--full", action="store_true", help="Download versi lengkap")
    parser.add_argument("--clean", action="store_true", help="Hapus data lama")
    parser.add_argument("--workers", type=int, default=4, help="Jumlah thread paralel")

    args = parser.parse_args()

    print("\n🚀 ML Agents Universe — HuggingFace Dataset Downloader")
    print(f"   Mode    : {'FULL' if args.full else 'SMALL (1000 rows)'}")
    print(f"   Workers : {args.workers} Parallel Threads")
    print(f"   Domains : {', '.join(args.domain)}\n")

    results = []

    # OPTIMASI: Parallel Downloading (Multi-threading)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_domain = {
            executor.submit(download_domain, domain, args.full, args.clean): domain
            for domain in args.domain
        }

        for future in as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                result = future.result()
                results.append(result)
                print(f"✅ [{domain}] Selesai diunduh.")
            except Exception as e:
                logger.error(f"Gagal memproses {domain}: {e}")
                results.append(
                    {
                        "domain": domain,
                        "status": "FAIL",
                        "rows": 0,
                        "columns": 0,
                        "file_size_kb": 0,
                        "time_sec": 0,
                        "path": "",
                    }
                )

    print_results_table(results)


if __name__ == "__main__":
    main()
