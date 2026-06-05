from pathlib import Path


base = Path("e:/dev/ml-agents-universe")

dirs_to_create = [
    "agents/nlp/src/agent",
    "agents/nlp/src/models",
    "agents/nlp/src/env",
    "agents/nlp/src/tools",
    "agents/nlp/configs",
    "agents/nlp/tests",

    "agents/finance/src/agent",
    "agents/finance/src/models",
    "agents/finance/src/env",
    "agents/finance/src/tools",
    "agents/finance/configs",
    "agents/finance/tests",

    "notebooks/nlp",
    "notebooks/finance",
]

for d in dirs_to_create:
    (base / d).mkdir(parents=True, exist_ok=True)

    # create __init__.py inside src folders
    if "src" in d or "tests" in d:
        (base / d / "__init__.py").touch(exist_ok=True)

# create empty notebooks
(base / "notebooks/nlp/00_eda.ipynb").write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')
(base / "notebooks/finance/00_eda.ipynb").write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')

print("Directories and basic files created.")
