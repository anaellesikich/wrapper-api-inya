# app/routes/v1/generate.py
from __future__ import annotations

import time
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from ...deps import require_api_key, get_gpt_client, get_request_context
from ...services.gpt_service import GPTClient
# If you wired the in-memory uploads in docs.py as shown earlier:
try:
    from .docs import SESSION_UPLOADS  # session_id -> extracted text
except Exception:  # if not present, keep things working
    SESSION_UPLOADS = {}

router = APIRouter()
log = logging.getLogger("app.routes.v1.generate")


# ----- Schemas -----

class Message(BaseModel):
    role: str = Field(..., description="user|assistant|system")
    content: str


class GenerateRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.6
    max_tokens: Optional[int] = 600
    stream: Optional[bool] = False
    session_id: Optional[str] = None  # to link ephemeral uploads


class GenerateResponse(BaseModel):
    content: str
    usage: dict | None = None
    model: str | None = None
    request_id: str
    latency_ms: int


# ----- Route -----

@router.post("/generate", response_model=GenerateResponse)
async def generate(
    body: GenerateRequest,
    _api_key: str = Depends(require_api_key),
    client: GPTClient = Depends(get_gpt_client),
):
    ctx = get_request_context()
    t0 = time.perf_counter()

    # Build base messages
    messages = [m.model_dump() for m in body.messages]

    # Pull ephemeral doc text for this session (if any) and pass as context_text
    context_text = ""
    if body.session_id:
        context_text = SESSION_UPLOADS.get(body.session_id, "") or ""

    try:
        # IMPORTANT: await and unpack the tuple
        content, usage, model = await client.generate(
            messages=messages,
            temperature=body.temperature or 0.6,
            max_tokens=body.max_tokens or 600,
            stream=False,  # streaming not implemented in this path
            session_id=body.session_id,
            context_text=context_text if context_text else None,
        )

        latency_ms = int((time.perf_counter() - t0) * 1000)
        return GenerateResponse(
            content=content or "",
            usage=usage or {},
            model=model,
            request_id=ctx["request_id"],
            latency_ms=latency_ms,
        )
    except Exception as e:
        log.exception("generate_failed: %s", e)
        # Surface a 502 so your frontend shows a clean error
        raise HTTPException(status_code=502, detail="Upstream generation failed")
