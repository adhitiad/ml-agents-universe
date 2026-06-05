# Education Agent

## Deskripsi

Agent untuk **Educational AI** — adaptive learning, knowledge tracing, student performance prediction, dan intelligent tutoring.

## Arsitektur

`
education/
├── src/
│   ├── agent/      # Tutoring agent & learning logic
│   ├── data/       # Student data processing
│   ├── models/     # Knowledge tracing models
│   ├── env/        # Learning environment
│   └── utils/      # Education-specific utilities
├── configs/        # YAML configuration files
├── data/           # Student & curriculum data
├── tests/          # Unit & integration tests
└── scripts/        # Automation scripts
`

## Setup & Instalasi

`ash
pip install -r requirements.txt
pip install -r agents/education/requirements.txt
`

## Penggunaan

`python
from agents.education.src.agent import EducationAgent

agent = EducationAgent()
recommendation = agent.recommend_next_topic(student_id="anon_001")
`

## Testing

`ash
pytest agents/education/tests/ -v
`

## Catatan Penting

> **WAJIB**: Student data harus ter-anonymize sebelum storage. Lihat `shared/utils` untuk anonymization helpers.
