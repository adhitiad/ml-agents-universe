#!/bin/bash
# ==========================================
# ML Agents Universe — Run All Tests
# ==========================================
# Penggunaan: bash scripts/run_all_tests.sh
# ==========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== ML Agents Universe — Test Suite ==="
echo "Project Root: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# 1. Lint check
echo "--- [1/4] Menjalankan Ruff Linter ---"
ruff check . || { echo "GAGAL: Ruff menemukan masalah."; exit 1; }
echo "[OK] Linting passed"
echo ""

# 2. Format check
echo "--- [2/4] Mengecek Formatting (Black) ---"
black --check . || { echo "GAGAL: Ada file yang belum di-format."; exit 1; }
echo "[OK] Formatting passed"
echo ""

# 3. Type check (non-blocking)
echo "--- [3/4] Type Checking (MyPy) ---"
mypy agents/ shared/ api/ --ignore-missing-imports || echo "[PERINGATAN] MyPy menemukan masalah (non-blocking)."
echo ""

# 4. Unit tests
echo "--- [4/4] Menjalankan Unit Tests ---"
pytest tests/ -v --tb=short --cov=agents --cov=shared --cov=api --cov-report=term-missing
echo ""

echo "=== Semua test selesai! ==="
