"""Data Ingestion for Finance."""
import asyncio
from typing import AsyncGenerator, Any
from datetime import datetime, timezone

async def extract_data() -> AsyncGenerator[dict[str, Any], None]:
    """Mock CCXT market data fetcher."""
    yield {"symbol": "BTC/USD", "price": 60000.5, "volume": 12.3, "timestamp": datetime.now(timezone.utc)}
    await asyncio.sleep(0.1)
    yield {"symbol": "ETH/USD", "price": 3000.0, "volume": 450.1, "timestamp": datetime.now(timezone.utc)}
