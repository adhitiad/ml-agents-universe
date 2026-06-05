from pathlib import Path


domains = [
    "nlp",
    "finance",
    "economy",
    "education",
    "entertainment",
    "mathematics",
    "science",
]
base = Path("e:/dev/ml-agents-universe")

for d in domains:
    (base / "data" / "raw" / d).mkdir(parents=True, exist_ok=True)
    (base / "data" / "processed" / d).mkdir(parents=True, exist_ok=True)
    (base / "data" / "schemas" / d).mkdir(parents=True, exist_ok=True)

    agent_data_dir = base / "agents" / d / "src" / "data"
    agent_data_dir.mkdir(parents=True, exist_ok=True)

    (base / "agents" / d / "src" / "__init__.py").touch(exist_ok=True)
    (agent_data_dir / "__init__.py").touch(exist_ok=True)

print("Directories and init files created successfully.")
