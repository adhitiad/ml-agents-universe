"""CLI untuk Manajemen API Key Terenkripsi.

Digunakan untuk menambah, menghapus, atau melihat daftar API key
yang tersimpan aman di dalam SQLite menggunakan Fernet Encryption.

Usage:
    python scripts/manage_keys.py --add groq "gsk_..."
    python scripts/manage_keys.py --delete groq
    python scripts/manage_keys.py --list
"""

import argparse
import os
import sys


# Force UTF-8 output di Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv
    # Load .env explicitly so KeyManager can see MASTER_ENCRYPTION_KEY
    load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")))
except ImportError:
    pass

from shared.models.key_manager import key_manager
from shared.models.llm_provider import LLMProvider


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Encrypted API Key Manager",
        epilog="""
Contoh:
  python scripts/manage_keys.py --add openai "sk-..."
  python scripts/manage_keys.py --list
  python scripts/manage_keys.py --delete anthropic
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--add", nargs=2, metavar=("PROVIDER", "KEY"), help="Tambah/Update API Key")
    parser.add_argument("--delete", metavar="PROVIDER", help="Hapus API Key")
    parser.add_argument("--list", action="store_true", help="Lihat daftar provider yang terkonfigurasi")

    args = parser.parse_args()

    # Pastikan valid provider
    valid_providers = [p.value for p in LLMProvider]

    if args.add:
        provider, key = args.add
        if provider not in valid_providers:
            print(f"[ERROR] Provider '{provider}' tidak valid. Pilih dari: {', '.join(valid_providers)}")
            return

        key_manager.set_key(provider, key)
        print(f"[SUCCESS] API Key untuk '{provider}' berhasil dienkripsi dan disimpan ke database.")
        return

    if args.delete:
        provider = args.delete
        if key_manager.delete_key(provider):
            print(f"[SUCCESS] API Key untuk '{provider}' berhasil dihapus dari database.")
        else:
            print(f"[WARNING] API Key untuk '{provider}' tidak ditemukan di database.")
        return

    if args.list:
        configured = key_manager.list_configured_providers()
        print("\n" + "=" * 50)
        print("  Encrypted API Keys di Database")
        print("=" * 50)

        if not configured:
            print("  [Kosong] Belum ada key yang disimpan.")
        else:
            for p in configured:
                print(f"  ✅ {p.ljust(15)} (Terenkripsi)")
        print("=" * 50 + "\n")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
