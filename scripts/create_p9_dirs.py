from pathlib import Path


base = Path("e:/dev/ml-agents-universe")

dirs_to_create = [
    "deployment/dockerfiles",
    "deployment/helm/ml-agents-universe/templates",
    "deployment/pipelines",
]

for d in dirs_to_create:
    path = base / d
    path.mkdir(parents=True, exist_ok=True)

print("Directories created for Phase 9.")
