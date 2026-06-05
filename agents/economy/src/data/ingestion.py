"""Data Ingestion for Economy."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock macro indicators fetcher."""
    yield {"country": "US", "indicator": "GDP", "value": 25000.0, "timestamp": datetime.now(timezone.utc)}
