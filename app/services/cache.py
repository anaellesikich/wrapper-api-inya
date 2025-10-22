import hashlib
import json
from typing import Optional

try:
    import redis
except ImportError:
    redis = None  # optional

class Cache:
    def __init__(self, url: Optional[str]):
        self.client = redis.Redis.from_url(url) if (url and redis) else None

    def available(self) -> bool:
        return self.client is not None

    def make_key(self, namespace: str, data: dict) -> str:
        digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        return f"{namespace}:{digest}"

    def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        val = self.client.get(key)
        return val.decode() if val else None

    def set(self, key: str, value: str, ttl: int = 60):
        if self.client:
            self.client.setex(key, ttl, value)
