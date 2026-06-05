# NLP Agent

## Deskripsi

Agent untuk **Natural Language Processing** (NLP) — pemrosesan bahasa natural, conversational AI, sentiment analysis, dan text mining.

## Arsitektur

`
nlp/
├── src/
│   ├── agent/      # LangGraph node definitions & agent logic
│   ├── data/       # Data loading, tokenization, preprocessing
│   ├── models/     # Pydantic schemas & ML model wrappers
│   ├── env/        # Environment configuration
│   └── utils/      # NLP-specific utilities
├── configs/        # YAML configuration files
├── data/           # Raw, processed, external data
├── models/         # Trained model artifacts
├── notebooks/      # Jupyter notebooks untuk EDA
├── api/            # Domain-specific API endpoints
├── tests/          # Unit & integration tests
└── scripts/        # Automation scripts
`

## Setup & Instalasi

`ash
# Dari root monorepo
pip install -r requirements.txt
pip install -r agents/nlp/requirements.txt
`

## Penggunaan

`python
from agents.nlp.src.agent import NLPAgent

agent = NLPAgent()
result = agent.process("Analisis sentimen teks ini")
`

## Testing

`ash
pytest agents/nlp/tests/ -v
`

## Konfigurasi

Lihat `configs/nlp/config.yaml` untuk konfigurasi domain-specific.

## Tech Stack

- **Transformers** (HuggingFace) — Pre-trained NLP models
- **NLTK** — Tokenization & linguistic analysis
- **BeautifulSoup4** — Web scraping untuk data collection
- **LangGraph** — Agent orchestration
