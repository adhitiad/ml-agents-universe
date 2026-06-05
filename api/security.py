import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verifikasi X-API-Key terhadap kunci yang diizinkan di .env."""
    # Daftar kunci yang diizinkan (dipisah koma)
    allowed_keys_str = os.getenv("API_ACCESS_KEYS", "master_key_123")
    allowed_keys = [k.strip() for k in allowed_keys_str.split(",") if k.strip()]

    if api_key not in allowed_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key tidak valid atau tidak disertakan.",
        )
    return api_key
