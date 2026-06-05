from pathlib import Path


base = Path("e:/dev/ml-agents-universe")

dirs_to_create = [
    "api",
    "shared/serving",
    "tests/api",
]

domains = [
    "nlp",
    "finance",
    "economy",
    "education",
    "entertainment",
    "mathematics",
    "science",
]
for d in domains:
    dirs_to_create.append(f"agents/{d}/api")

for d in dirs_to_create:
    path = base / d
    path.mkdir(parents=True, exist_ok=True)
    (path / "__init__.py").touch(exist_ok=True)

print("Directories and __init__ files created for Phase 7.")
