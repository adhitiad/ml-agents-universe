from pathlib import Path


base = Path("e:/dev/ml-agents-universe")

dirs_to_create = [
    # Entertainment
    "agents/entertainment/src/agent",
    "agents/entertainment/src/models",
    "agents/entertainment/src/env",
    "agents/entertainment/src/tools",
    "agents/entertainment/tests",
    "notebooks/entertainment",

    # Mathematics
    "agents/mathematics/src/agent",
    "agents/mathematics/src/models",
    "agents/mathematics/src/env",
    "agents/mathematics/src/tools",
    "agents/mathematics/tests",
    "notebooks/mathematics",

    # Science
    "agents/science/src/agent",
    "agents/science/src/models",
    "agents/science/src/env",
    "agents/science/src/tools",
    "agents/science/tests",
    "agents/science/experiments",
    "notebooks/science",
]

for d in dirs_to_create:
    (base / d).mkdir(parents=True, exist_ok=True)

    # create __init__.py inside src and tests folders
    if "src" in d or "tests" in d:
        (base / d / "__init__.py").touch(exist_ok=True)

# create empty notebooks
(base / "notebooks/entertainment/00_eda.ipynb").write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')
(base / "notebooks/mathematics/00_eda.ipynb").write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')
(base / "notebooks/science/00_eda.ipynb").write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')

print("Directories and basic files created for Phase 6.")
