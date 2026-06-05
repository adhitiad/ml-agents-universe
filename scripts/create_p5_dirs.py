from pathlib import Path


base = Path("e:/dev/ml-agents-universe")

dirs_to_create = [
    "agents/economy/src/agent",
    "agents/economy/src/models",
    "agents/economy/src/env",
    "agents/economy/src/tools",
    "agents/economy/simulations",
    "agents/economy/outputs",
    "agents/economy/tests",

    "agents/education/src/agent",
    "agents/education/src/models",
    "agents/education/src/env",
    "agents/education/src/tools",
    "agents/education/configs",
    "agents/education/tests",

    "notebooks/economy",
    "notebooks/education",
]

for d in dirs_to_create:
    (base / d).mkdir(parents=True, exist_ok=True)

    # create __init__.py inside src folders
    if "src" in d or "tests" in d or "outputs" in d:
        (base / d / "__init__.py").touch(exist_ok=True)

# create empty notebooks
(base / "notebooks/economy/00_eda.ipynb").write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')
(base / "notebooks/education/00_eda.ipynb").write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":5}')

print("Directories and basic files created for Phase 5.")
