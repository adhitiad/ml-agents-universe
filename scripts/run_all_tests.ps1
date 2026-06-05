# ==========================================
# ML Agents Universe — Run All Tests (PowerShell)
# ==========================================
# Penggunaan: .\scripts\run_all_tests.ps1
# ==========================================

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== ML Agents Universe — Test Suite ===" -ForegroundColor Yellow
Write-Host "Project Root: $ProjectRoot"
Write-Host ""

Set-Location $ProjectRoot

# 1. Lint check
Write-Host "--- [1/4] Menjalankan Ruff Linter ---" -ForegroundColor Cyan
ruff check .
if ($LASTEXITCODE -ne 0) {
    Write-Host "GAGAL: Ruff menemukan masalah." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Linting passed" -ForegroundColor Green
Write-Host ""

# 2. Format check
Write-Host "--- [2/4] Mengecek Formatting (Black) ---" -ForegroundColor Cyan
black --check .
if ($LASTEXITCODE -ne 0) {
    Write-Host "GAGAL: Ada file yang belum di-format." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Formatting passed" -ForegroundColor Green
Write-Host ""

# 3. Type check (non-blocking)
Write-Host "--- [3/4] Type Checking (MyPy) ---" -ForegroundColor Cyan
mypy agents/ shared/ api/ --ignore-missing-imports
if ($LASTEXITCODE -ne 0) {
    Write-Host "[PERINGATAN] MyPy menemukan masalah (non-blocking)." -ForegroundColor Yellow
}
Write-Host ""

# 4. Unit tests
Write-Host "--- [4/4] Menjalankan Unit Tests ---" -ForegroundColor Cyan
pytest tests/ -v --tb=short --cov=agents --cov=shared --cov=api --cov-report=term-missing
Write-Host ""

Write-Host "=== Semua test selesai! ===" -ForegroundColor Green
