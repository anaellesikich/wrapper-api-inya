from fastapi import Header, HTTPException, status
from typing import Optional
from ..config import settings

async def api_key_auth(x_api_key: Optional[str] = Header(default=None)) -> str:
    if not x_api_key or x_api_key not in settings.API_KEYS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return x_api_key
