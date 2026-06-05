"""Data Ingestion for Mathematics."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock theorem database API."""
    yield {"theorem_id": "th1", "statement": "a^2 + b^2 = c^2", "proven": True, "timestamp": datetime.now(timezone.utc)}
