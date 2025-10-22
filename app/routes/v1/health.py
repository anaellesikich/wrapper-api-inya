from fastapi import APIRouter
from ...config import settings
from ...services.cache import Cache

router = APIRouter()

@router.get("/health")
async def health():
    """
    Health check endpoint. Returns app status and environment info.
    """
    return {
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "redis": bool(Cache(settings.REDIS_URL).available()),
        "provider": settings.GPT_PROVIDER,
        "status": "ok",
    }

