# app/deps.py
"""
Dependency wiring for the FastAPI app.

- require_api_key: enforces X-API-Key header
- get_request_context: per-request metadata (request_id, start time)
- get_gpt_client: returns an OpenAI client; prefers Assistants API when OPENAI_ASSISTANT_ID is set
- get_cache: shared cache handle (noop if REDIS_URL is empty)
"""

import time
import uuid
import logging
from fastapi import Depends

from .utils.auth import api_key_auth
from .config import settings
from .services.cache import Cache
from .services.gpt_service import EchoClient, OpenAIClient, GPTClient

log = logging.getLogger("app.deps")

# Single cache instance (safe for local/dev; swap for managed Redis in prod)
_cache = Cache(settings.REDIS_URL)


async def require_api_key(api_key: str = Depends(api_key_auth)) -> str:
    """Enforce API key on protected routes."""
    return api_key


def get_request_context() -> dict:
    """Attach a request id and start time for logging/metrics."""
    return {"request_id": str(uuid.uuid4()), "start": time.perf_counter()}


def get_gpt_client() -> GPTClient:
    """
    Return the GPT client.
    - If GPT_PROVIDER=openai and OPENAI_API_KEY is set:
        * If OPENAI_ASSISTANT_ID is set -> use Assistants (Responses API) via OpenAIClient(assistant_id=...)
        * Else -> fall back to plain chat.completions
    - Else -> EchoClient (dev stub)
    """
    if settings.GPT_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        client = OpenAIClient(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            assistant_id=settings.OPENAI_ASSISTANT_ID,  # <<< ensures Assistant is used when present
        )
        mode = "assistant" if settings.OPENAI_ASSISTANT_ID else "chat"
        log.info("get_gpt_client -> OpenAIClient mode=%s model=%s", mode, settings.OPENAI_MODEL)
        return client

    log.info("get_gpt_client -> EchoClient (dev)")
    return EchoClient()


def get_cache() -> Cache:
    """Return the process-wide cache instance (noop if REDIS_URL unset)."""
    return _cache
