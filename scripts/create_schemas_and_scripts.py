from pathlib import Path

import yaml


base = Path("e:/dev/ml-agents-universe")

domains = {
    "nlp": {
        "schema": {
            "name": "corpus",
            "version": "1.0.0",
            "domain": "nlp",
            "columns": [
                {"name": "id", "type": "string", "nullable": False},
                {"name": "text", "type": "string", "nullable": False},
                {"name": "source", "type": "string", "nullable": True},
                {"name": "timestamp", "type": "datetime", "nullable": True},
            ]
        },
        "ingestion_code": '''"""Data Ingestion for NLP."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock web scraping."""
    yield {"id": "doc1", "text": "Hello world from NLP.", "source": "web", "timestamp": datetime.now(timezone.utc)}
    await asyncio.sleep(0.1)
    yield {"id": "doc2", "text": "Another parsed document.", "source": "web", "timestamp": datetime.now(timezone.utc)}
'''
    },
    "finance": {
        "schema": {
            "name": "market_data",
            "version": "1.0.0",
            "domain": "finance",
            "columns": [
                {"name": "symbol", "type": "string", "nullable": False},
                {"name": "price", "type": "float", "nullable": False, "constraints": {"min": 0}},
                {"name": "volume", "type": "float", "nullable": True},
                {"name": "timestamp", "type": "datetime", "nullable": False},
            ]
        },
        "ingestion_code": '''"""Data Ingestion for Finance."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock CCXT market data fetcher."""
    yield {"symbol": "BTC/USD", "price": 60000.5, "volume": 12.3, "timestamp": datetime.now(timezone.utc)}
    await asyncio.sleep(0.1)
    yield {"symbol": "ETH/USD", "price": 3000.0, "volume": 450.1, "timestamp": datetime.now(timezone.utc)}
'''
    },
    "economy": {
        "schema": {
            "name": "macro_indicators",
            "version": "1.0.0",
            "domain": "economy",
            "columns": [
                {"name": "country", "type": "string", "nullable": False},
                {"name": "indicator", "type": "string", "nullable": False},
                {"name": "value", "type": "float", "nullable": False},
                {"name": "timestamp", "type": "datetime", "nullable": False},
            ]
        },
        "ingestion_code": '''"""Data Ingestion for Economy."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock macro indicators fetcher."""
    yield {"country": "US", "indicator": "GDP", "value": 25000.0, "timestamp": datetime.now(timezone.utc)}
'''
    },
    "education": {
        "schema": {
            "name": "student_logs",
            "version": "1.0.0",
            "domain": "education",
            "columns": [
                {"name": "student_id", "type": "string", "nullable": False},
                {"name": "action", "type": "string", "nullable": False},
                {"name": "score", "type": "float", "nullable": True, "constraints": {"min": 0, "max": 100}},
                {"name": "timestamp", "type": "datetime", "nullable": False},
            ]
        },
        "ingestion_code": '''"""Data Ingestion for Education."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock student interaction logs."""
    yield {"student_id": "s1", "action": "quiz_submit", "score": 85.5, "timestamp": datetime.now(timezone.utc)}
'''
    },
    "entertainment": {
        "schema": {
            "name": "user_behavior",
            "version": "1.0.0",
            "domain": "entertainment",
            "columns": [
                {"name": "user_id", "type": "string", "nullable": False},
                {"name": "content_id", "type": "string", "nullable": False},
                {"name": "duration_sec", "type": "integer", "nullable": False, "constraints": {"min": 0}},
                {"name": "timestamp", "type": "datetime", "nullable": False},
            ]
        },
        "ingestion_code": '''"""Data Ingestion for Entertainment."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock user behavior logs."""
    yield {"user_id": "u1", "content_id": "c1", "duration_sec": 120, "timestamp": datetime.now(timezone.utc)}
'''
    },
    "mathematics": {
        "schema": {
            "name": "theorem_db",
            "version": "1.0.0",
            "domain": "mathematics",
            "columns": [
                {"name": "theorem_id", "type": "string", "nullable": False},
                {"name": "statement", "type": "string", "nullable": False},
                {"name": "proven", "type": "boolean", "nullable": False},
                {"name": "timestamp", "type": "datetime", "nullable": True},
            ]
        },
        "ingestion_code": '''"""Data Ingestion for Mathematics."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock theorem database API."""
    yield {"theorem_id": "th1", "statement": "a^2 + b^2 = c^2", "proven": True, "timestamp": datetime.now(timezone.utc)}
'''
    },
    "science": {
        "schema": {
            "name": "molecular_data",
            "version": "1.0.0",
            "domain": "science",
            "columns": [
                {"name": "molecule_id", "type": "string", "nullable": False},
                {"name": "smiles", "type": "string", "nullable": False},
                {"name": "weight", "type": "float", "nullable": True, "constraints": {"min": 0}},
                {"name": "timestamp", "type": "datetime", "nullable": True},
            ]
        },
        "ingestion_code": '''"""Data Ingestion for Science."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock molecular data fetcher."""
    yield {"molecule_id": "mol1", "smiles": "CCO", "weight": 46.07, "timestamp": datetime.now(timezone.utc)}
'''
    }
}

for d_name, d_data in domains.items():
    # Write Schema YAML
    schema_dir = base / "data" / "schemas" / d_name
    schema_dir.mkdir(parents=True, exist_ok=True)
    schema_file = schema_dir / f"{d_data['schema']['name']}.yaml"
    with schema_file.open("w", encoding="utf-8") as f:
        yaml.dump(d_data['schema'], f, sort_keys=False)

    # Write ingestion.py
    ingestion_dir = base / "agents" / d_name / "src" / "data"
    ingestion_dir.mkdir(parents=True, exist_ok=True)
    ingestion_file = ingestion_dir / "ingestion.py"
    with ingestion_file.open("w", encoding="utf-8") as f:
        f.write(d_data['ingestion_code'])

print("Schemas and ingestion scripts created successfully.")
