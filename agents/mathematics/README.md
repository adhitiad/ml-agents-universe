# Mathematics Agent

## Deskripsi

Agent untuk **Mathematical Problem Solving** — symbolic computation, theorem proving, equation solving, dan mathematical reasoning.

## Arsitektur

`
mathematics/
├── src/
│   ├── agent/      # Math solver agent logic
│   ├── data/       # Theorem & problem datasets
│   ├── models/     # Mathematical models & solvers
│   ├── env/        # Solver configuration
│   └── utils/      # Math-specific utilities
├── configs/        # YAML configuration files
├── data/           # Theorem & proof data
├── tests/          # Unit & integration tests
└── scripts/        # Automation scripts
`

## Setup & Instalasi

`ash
pip install -r requirements.txt
pip install -r agents/mathematics/requirements.txt
`

## Penggunaan

`python
from agents.mathematics.src.agent import MathematicsAgent

agent = MathematicsAgent()
solution = agent.solve("x^2 + 2x - 3 = 0")
`

## Testing

`ash
pytest agents/mathematics/tests/ -v
`

## Konfigurasi

Lihat `configs/mathematics/config.yaml` untuk solver parameters.
