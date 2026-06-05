# Economy Agent

## Deskripsi

Agent untuk **Economic Simulation** — agent-based economic modeling, macro indicator analysis, dan economic forecasting.

## Arsitektur

`
economy/
├── src/
│   ├── agent/      # Economic simulation agents
│   ├── data/       # Macro data loading
│   ├── models/     # Economic models & forecasting
│   ├── env/        # Simulation environment
│   └── utils/      # Economic calculation utilities
├── simulations/    # Simulation output data
├── outputs/        # Analysis results & reports
├── configs/        # YAML configuration files
├── data/           # Economic data (raw & processed)
├── tests/          # Unit & integration tests
└── scripts/        # Automation scripts
`

## Setup & Instalasi

`ash
pip install -r requirements.txt
pip install -r agents/economy/requirements.txt
`

## Penggunaan

`python
from agents.economy.src.agent import EconomyAgent

agent = EconomyAgent()
forecast = agent.forecast_gdp(country="ID", horizon=4)
`

## Testing

`ash
pytest agents/economy/tests/ -v
`

## Konfigurasi

Lihat `configs/economy/config.yaml` untuk simulation parameters.
