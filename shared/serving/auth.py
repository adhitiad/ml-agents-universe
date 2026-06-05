"""Sistem Autentikasi API Key."""

from fastapi import HTTPException, status
from fastapi.requests import HTTPConnection


# Mock database of allowed keys
ALLOWED_KEYS = {
    "dev_universe_key": "admin",
}


def verify_api_key(conn: HTTPConnection) -> str:
    """Verifikasi API Key dari header."""
    api_key = conn.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key in header.",
        )
    if api_key not in ALLOWED_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key.",
        )
    return api_key
