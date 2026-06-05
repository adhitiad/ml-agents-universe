# 🌌 ML Agents Universe

> **Monorepo untuk multi-domain AI agent orchestration menggunakan LangGraph dengan dukungan Aplikasi Desktop.**

ML Agents Universe adalah sistem multi-agent yang mengorkestrasi 7 domain AI agent spesialis melalui arsitektur supervisor berbasis LangGraph. Setiap agent memiliki kemampuan domain-specific dan dapat berkolaborasi untuk menyelesaikan tugas kompleks. Dilengkapi juga dengan aplikasi desktop (PySide6) yang terintegrasi dengan fitur voice command, hotkey global, dan manajemen plugin.

---

## 🏗️ Arsitektur

```text
                    ┌─────────────┐
                    │  Supervisor │
                    │   (Router)  │
                    └──────┬──────┘
                           │
          ┌────────┬───────┼───────┬────────┐
          ▼        ▼       ▼       ▼        ▼
      ┌──────┐ ┌──────┐ ┌─────┐ ┌──────┐ ┌─────┐
      │  NLP │ │ FIN  │ │ ECO │ │ EDU  │ │ ... │
      └──────┘ └──────┘ └─────┘ └──────┘ └─────┘
```

Supervisor menerima input pengguna dan merutekan ke domain agent yang tepat. Setiap agent memproses task secara independen menggunakan tools dan models domain-specific.

---

## 📁 Struktur Monorepo

```text
ml-agents-universe/
├── agents/                    # Domain-specific agents
│   ├── nlp/                   # Natural Language Processing
│   ├── finance/               # Financial Analysis & Trading
│   ├── economy/               # Economic Simulation
│   ├── education/             # Educational AI & Tutoring
│   ├── entertainment/         # Content Recommendation
│   ├── mathematics/           # Mathematical Problem Solving
│   └── science/               # Scientific Discovery
├── shared/                    # Shared library (base classes, utils)
│   ├── data/                  # Data loading & validation
│   ├── models/                # Base agent & Pydantic schemas
│   ├── env/                   # Environment configuration
│   ├── serving/               # API serving utilities
│   ├── monitoring/            # Logging & health checks
│   └── utils/                 # Common helper functions
├── api/                       # FastAPI router & endpoints
├── ui/                        # PySide6 Desktop App UI components
├── configs/                   # YAML configurations per domain
├── data/                      # Data lake (raw, processed, schemas)
├── tests/                     # Test suite
├── deployment/                # Docker, Helm, CI/CD pipelines
├── notebooks/                 # Jupyter notebooks per domain
└── scripts/                   # Automation scripts
```

---

## 🚀 Fitur Utama

- **Multi-Agent Orchestration**: 7 domain agent independen yang diorkestrasi oleh LangGraph Supervisor.
- **Aplikasi Desktop Terintegrasi**: Dibangun dengan PySide6, mendukung antarmuka grafis yang ramah pengguna.
- **Produktivitas Desktop**: Mendukung Global Hotkey (`Alt+Space` untuk buka/tutup), System Tray, Voice Commands terintegrasi.
- **Plugin Store**: Sistem plugin modular untuk kustomisasi lebih lanjut langsung dari aplikasi.
- **Docker & Microservices**: Siap dideploy menggunakan `docker-compose`.
- **Standalone Build**: Kompilasi ke binary executable ringan menggunakan Nuitka.

---

## 🚀 Quick Start

### 1. Clone & Setup Environment

```bash
git clone <repo-url> ml-agents-universe
cd ml-agents-universe

# Buat virtual environment
python -m venv venv

# Aktivasi (Windows)
.\venv\Scripts\activate

# Aktivasi (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install semua dependencies (termasuk PySide6, Nuitka, LangGraph, dll)
pip install -r requirements.txt

# Install dev tools (opsional)
pip install -e ".[dev]"
```

### 3. Setup Environment Variables

```bash
# Salin template .env
cp .env.example .env

# Edit .env dengan nilai yang sesuai
# Terutama: OLLAMA_BASE_URL, OLLAMA_MODEL_NAME
```

### 4. Menjalankan Aplikasi Desktop

Menjalankan UI desktop interaktif dengan Setup Wizard (jika belum dikonfigurasi).

```bash
python run_desktop.py
```

### 5. Menjalankan Backend API (Standalone)

Jika hanya ingin menjalankan backend API / Router tanpa antarmuka desktop:

```bash
python api/router.py
```

### 6. Deployment dengan Docker Compose

Untuk mendeploy seluruh layanan (API Gateway dan 7 microservice agents) ke environment terisolasi:

```bash
docker-compose up -d --build
```

### 7. Membangun Executable File

Anda dapat membangun aplikasi menjadi satu file executable mandiri (.exe) tanpa memerlukan environment Python tambahan bagi user menggunakan Nuitka:

```bash
# Untuk Windows
build_nuitka.bat
```

---

## 🛠️ Development Workflow

### Linting & Formatting

```bash
# Jalankan linter
make lint

# Auto-fix lint issues
make lint-fix

# Format code
make format

# Cek formatting tanpa mengubah
make format-check
```

### Testing

```bash
# Jalankan semua tests
make test

# Tests dengan coverage
make test-cov

# Test domain tertentu
make test-domain DOMAIN=nlp
```

### Pre-commit Hooks

```bash
# Install hooks (sekali saja)
pre-commit install

# Jalankan pada semua file
make pre-commit
```

---

## 🤖 Domain Agents

| Domain | Deskripsi | Tech Stack |
|---|---|---|
| **NLP** | Pemrosesan bahasa natural, sentiment analysis, Q&A | Transformers, NLTK, BeautifulSoup4 |
| **Finance** | Trading strategies, market analysis, portfolio mgmt | CCXT, Pandas, NumPy |
| **Economy** | Economic simulation, macro analysis, forecasting | Polars, SciPy, scikit-learn |
| **Education** | Adaptive learning, knowledge tracing, tutoring | scikit-learn, PyTorch |
| **Entertainment** | Content recommendation, personalization | scikit-learn, Polars |
| **Mathematics** | Problem solving, theorem proving, symbolic computation | SciPy, NumPy |
| **Science** | Experiment design, molecular analysis, literature mining | SciPy, RDKit |
| **Healthcare** | Menganalisis gejala awal, ringkasan jurnal medis, cek interaksi obat | scikit-learn, Pandas |
| **Legal** | Menganalisis kontrak, merangkum ToS, compliance checking | Transformers, spaCy |
| **Cybersecurity** | Log analysis, vulnerability scan recommendations, threat intelligence | Pandas, scikit-learn |
| **Creative** | UI/UX brainstorming, cerita interaktif, perakit prompt canggih | Transformers, Pillow |
| **DevOps** | CI/CD pipeline suggestions, k8s/Docker config generation | PyYAML, regex |
| **Data Eng** | Auto-cleansing, schema inference, ETL script generation | Polars, Pandas |
| **OSINT** | Trend sentiment analysis, viral news summary, fact-checking | BeautifulSoup4, Transformers |
| **Game AI** | NPC behavior design, game balancing, procedural content gen | SciPy, NumPy |
| **Productivity** | Calendar management, email thread summary, priority to-do | Transformers, pandas |

---

## ⚙️ Konfigurasi

- **Global**: `configs/global.yaml` — pengaturan aplikasi, logging, data lake
- **Per Domain**: `configs/{domain}/config.yaml` — pengaturan spesifik per agent
- **Environment**: `.env` — secrets dan API keys (JANGAN commit!)
- **Desktop**: `data/desktop_config.json` — otomatis terbuat setelah Setup Wizard

---

## 📋 Aturan Development

1. ✅ Gunakan **Python 3.11+ type hints** di semua function signatures
2. ✅ Gunakan **Pydantic v2** untuk semua data models
3. ✅ Gunakan **absolute imports** dari root package
4. ✅ Setiap file Python harus memiliki **module docstring**
5. ✅ Gunakan **`Decimal`** untuk financial calculations, bukan `float`
6. ✅ **Anonymize** student data sebelum storage
7. ❌ **JANGAN** hardcode secrets — gunakan `.env`
8. ❌ **JANGAN** gunakan `print()` di production code — gunakan `logging`

---

## 📝 License

MIT License — Lihat [LICENSE](LICENSE) untuk detail.
