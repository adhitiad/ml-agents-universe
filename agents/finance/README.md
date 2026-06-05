# Finance Agent

## Deskripsi

Agent untuk **Financial Analysis** — trading strategies, market data analysis, portfolio management, dan risk assessment.

## Arsitektur

`
finance/
├── src/
│   ├── agent/      # Trading agent & market analysis logic
│   ├── data/       # Market data fetching (CCXT)
│   ├── models/     # Price prediction & risk models
│   ├── env/        # Exchange & API configuration
│   └── utils/      # Financial calculation utilities
├── configs/        # YAML configuration files
├── data/           # Market data (raw & processed)
├── models/         # Trained model artifacts
├── notebooks/      # Backtesting notebooks
├── api/            # Trading API endpoints
├── tests/          # Unit & integration tests
└── scripts/        # Automation scripts
`

## Setup & Instalasi

`ash
pip install -r requirements.txt
pip install -r agents/finance/requirements.txt
`

## Penggunaan

`python
from agents.finance.src.agent import FinanceAgent

agent = FinanceAgent()
analysis = agent.analyze_market("BTC/USDT", timeframe="1h")
`

## Testing

`ash
pytest agents/finance/tests/ -v
`

## Konfigurasi

Lihat `configs/finance/config.yaml` untuk konfigurasi exchange dan trading parameters.

## Catatan Penting

> **WAJIB**: Semua financial calculations harus menggunakan `Decimal` type, bukan `float`.
> API keys exchange harus disimpan di `.env`, JANGAN di-hardcode.
