"""Data Ingestion for NLP."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock web scraping."""
    yield {"id": "doc1", "text": "Hello world from NLP.", "source": "web", "timestamp": datetime.now(timezone.utc)}
    await asyncio.sleep(0.1)
    yield {"id": "doc2", "text": "Another parsed document.", "source": "web", "timestamp": datetime.now(timezone.utc)}
