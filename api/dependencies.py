"""API Dependencies (Rate Limiting & Auth Injection)."""

import time

from fastapi import Depends, HTTPException, status
from fastapi.requests import HTTPConnection

from shared.serving.auth import verify_api_key


# In-Memory Simple Rate Limiter (e.g. 5 requests per 10 seconds per API Key)
RATE_LIMIT_DURATION = 10
MAX_REQUESTS = 5

request_history = {}


def rate_limiter(conn: HTTPConnection, api_key: str = Depends(verify_api_key)):
    """Simple Sliding Window Rate Limiter based on API Key."""
    current_time = time.time()

    # Initialize list if not exist
    if api_key not in request_history:
        request_history[api_key] = []

    # Remove old timestamps outside the window
    request_history[api_key] = [
        t for t in request_history[api_key] if current_time - t < RATE_LIMIT_DURATION
    ]

    if len(request_history[api_key]) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(RATE_LIMIT_DURATION)},
        )

    # Add current request
    request_history[api_key].append(current_time)

    return api_key
