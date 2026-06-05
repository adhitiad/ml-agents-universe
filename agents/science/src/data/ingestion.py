"""Data Ingestion for Science."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock molecular data fetcher."""
    yield {"molecule_id": "mol1", "smiles": "CCO", "weight": 46.07, "timestamp": datetime.now(timezone.utc)}
