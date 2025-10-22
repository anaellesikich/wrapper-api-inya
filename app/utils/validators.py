from pydantic import BaseModel, Field, conint, confloat
from typing import Any, Dict, List, Optional

class Message(BaseModel):
    role: str = Field(pattern=r"^(system|user|assistant)$")
    content: str = Field(min_length=1, max_length=8000)

class GenerateRequest(BaseModel):
    messages: List[Message]
    temperature: confloat(ge=0.0, le=2.0) = 0.7
    max_tokens: conint(ge=1, le=4096) = 512
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    stream: bool = False

class GenerateResponse(BaseModel):
    request_id: str
    content: str
    usage: Dict[str, int]
    model: str
    latency_ms: int
