"""Script untuk menjalankan ML Agents Universe API Server.

Usage:
    python scripts/run_server.py                      # Default: localhost:8000
    python scripts/run_server.py --port 8080           # Port custom
    python scripts/run_server.py --host 0.0.0.0        # Expose ke network
    python scripts/run_server.py --reload               # Auto-reload saat development
"""

from __future__ import annotations

import argparse
import os
import sys


# Menambahkan root direktori ke sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force UTF-8 output di Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]


def main() -> None:
    """Entry point untuk menjalankan API server."""
    parser = argparse.ArgumentParser(
        description="ML Agents Universe — API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python scripts/run_server.py                        # Default localhost:8000
  python scripts/run_server.py --port 8080             # Port custom
  python scripts/run_server.py --host 0.0.0.0 --reload  # Dev mode
        """,
    )

    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("FASTAPI_HOST", "127.0.0.1"),
        help="Host address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("FASTAPI_PORT", "8000")),
        help="Port number (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development mode)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)",
    )

    args = parser.parse_args()

    # Info startup
    print(f"\n{'=' * 60}")
    print("  ML Agents Universe — API Server")
    print(f"{'=' * 60}")
    print(f"  Host:    {args.host}")
    print(f"  Port:    {args.port}")
    print(f"  Reload:  {args.reload}")
    print(f"  Workers: {args.workers}")
    print(f"  LLM:     {os.getenv('LLM_PROVIDER', 'ollama')} / {os.getenv('LLM_MODEL', 'uis_quan')}")
    print(f"{'=' * 60}")
    print(f"\n  API Docs:  http://{args.host}:{args.port}/docs")
    print(f"  Health:    http://{args.host}:{args.port}/health")
    print(f"  Metrics:   http://{args.host}:{args.port}/metrics\n")

    import uvicorn

    uvicorn.run(
        "api.gateway:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
