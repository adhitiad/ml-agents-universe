# Science Agent

## Deskripsi

Agent untuk **Scientific Discovery** — experiment design, molecular analysis, literature mining, dan scientific reasoning.

## Arsitektur

`
science/
├── src/
│   ├── agent/      # Scientific reasoning agent
│   ├── data/       # Experiment & literature data
│   ├── models/     # Scientific models
│   ├── env/        # Lab environment configuration
│   └── utils/      # Science-specific utilities
├── experiments/    # Experiment results & logs
├── configs/        # YAML configuration files
├── data/           # Molecular & literature data
├── tests/          # Unit & integration tests
└── scripts/        # Automation scripts
`

## Setup & Instalasi

`ash
pip install -r requirements.txt
pip install -r agents/science/requirements.txt
`

## Penggunaan

`python
from agents.science.src.agent import ScienceAgent

agent = ScienceAgent()
analysis = agent.analyze_molecule("C6H12O6")
`

## Testing

`ash
pytest agents/science/tests/ -v
`

## Konfigurasi

Lihat `configs/science/config.yaml` untuk experiment parameters.
