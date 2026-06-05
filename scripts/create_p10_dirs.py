from pathlib import Path


base = Path("e:/dev/ml-agents-universe")

dirs_to_create = [
    "shared/monitoring",
    "deployment/monitoring/alerts",
    "deployment/monitoring/dashboards",
    "docs/runbooks"
]

for d in dirs_to_create:
    path = base / d
    path.mkdir(parents=True, exist_ok=True)
    if "shared" in d:
        (path / "__init__.py").touch(exist_ok=True)

print("Directories created for Phase 10.")
