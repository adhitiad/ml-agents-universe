"""Data Ingestion for Entertainment."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock user behavior logs."""
    yield {"user_id": "u1", "content_id": "c1", "duration_sec": 120, "timestamp": datetime.now(timezone.utc)}
