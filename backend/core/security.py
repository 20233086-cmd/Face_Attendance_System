import secrets

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from backend.core.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(_api_key_header)) -> str:
    """So sánh API key gửi lên (header X-API-Key) với API key cấu hình trong .env."""
    if not api_key or not secrets.compare_digest(api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key không hợp lệ hoặc thiếu header X-API-Key",
        )
    return api_key
