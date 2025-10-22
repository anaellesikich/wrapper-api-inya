from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional
import json


class Settings(BaseSettings):
    APP_NAME: str = "my-gpt-wrapper"
    APP_ENV: str = "dev"  # dev|staging|prod
    LOG_LEVEL: str = "INFO"

    # CORS
    ALLOW_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Auth
    API_KEYS: List[str] = ["dev-secret-key"]  # replace in prod

    # Provider
    GPT_PROVIDER: str = "echo"  # echo|openai|local
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Assistant (added)
    OPENAI_ASSISTANT_ID: Optional[str] = None
    OPENAI_VECTOR_STORE_ID: Optional[str] = None

    # Cache (optional)
    REDIS_URL: Optional[str] = None
    REQUEST_TIMEOUT_S: float = 30.0

    # Config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # ignore unknown env vars instead of erroring
    )

    @field_validator("ALLOW_ORIGINS", "API_KEYS", mode="before")
    @classmethod
    def _parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                # fallback for comma-separated strings
                return [s.strip() for s in v.split(",") if s.strip()]
        return v


settings = Settings()
