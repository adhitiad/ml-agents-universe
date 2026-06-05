# ==========================================
# ML AGENTS UNIVERSE — Makefile
# ==========================================
# Penggunaan: make <target>
# ==========================================

.PHONY: help install install-dev lint lint-fix format format-check test test-cov clean verify all pre-commit

# Default target
help: ## Tampilkan daftar target yang tersedia
	@echo "=== ML Agents Universe — Makefile ==="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Installation ---

install: ## Install semua dependencies dari requirements.txt
	pip install -r requirements.txt

install-dev: ## Install dependencies development (pytest, black, ruff, pre-commit)
	pip install -e ".[dev]"
	pre-commit install

# --- Linting ---

lint: ## Jalankan ruff linter
	ruff check .

lint-fix: ## Jalankan ruff linter dengan auto-fix
	ruff check --fix .

# --- Formatting ---

format: ## Format code dengan black dan ruff
	black .
	ruff format .

format-check: ## Cek formatting tanpa mengubah file
	black --check .
	ruff format --check .

# --- Testing ---

test: ## Jalankan semua test dengan pytest
	pytest tests/ -v

test-cov: ## Jalankan test dengan coverage report
	pytest tests/ -v --cov=agents --cov=shared --cov=api --cov-report=term-missing

test-domain: ## Jalankan test untuk domain tertentu (usage: make test-domain DOMAIN=nlp)
	pytest tests/agents/$(DOMAIN)/ -v

# --- Type Checking ---

typecheck: ## Jalankan mypy type checker
	mypy agents/ shared/ api/ --ignore-missing-imports

# --- Cleanup ---

clean: ## Hapus file cache dan build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist/ build/ .coverage htmlcov/

# --- Verification ---

verify: ## Verifikasi bahwa semua dependencies terinstal dengan benar
	@echo "=== Verifikasi Dependencies ==="
	python -c "import langgraph; print(f'  [OK] langgraph {langgraph.__version__}')"
	python -c "import fastapi; print(f'  [OK] fastapi {fastapi.__version__}')"
	python -c "import pydantic; print(f'  [OK] pydantic {pydantic.__version__}')"
	python -c "import langchain_core; print(f'  [OK] langchain-core {langchain_core.__version__}')"
	python -c "import polars; print(f'  [OK] polars {polars.__version__}')"
	python -c "import yaml; print(f'  [OK] PyYAML {yaml.__version__}')"
	python -c "import dotenv; print(f'  [OK] python-dotenv {dotenv.__version__}')"
	@echo ""
	@echo "=== Verifikasi Internal Packages ==="
	python -c "import shared; print(f'  [OK] shared {shared.__version__}')"
	@echo ""
	@echo "=== Semua verifikasi berhasil! ==="

# --- Pre-commit ---

pre-commit: ## Jalankan pre-commit hooks pada semua file
	pre-commit run --all-files

# --- All-in-One ---

all: lint format test ## Jalankan lint, format, dan test sekaligus
	@echo ""
	@echo "=== Semua check selesai! ==="
