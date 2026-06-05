"""Data Ingestion for Education."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock student interaction logs."""
    yield {"student_id": "s1", "action": "quiz_submit", "score": 85.5, "timestamp": datetime.now(timezone.utc)}
