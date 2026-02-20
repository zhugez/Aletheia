from __future__ import annotations

import hashlib
import json
import os
from typing import Any

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


class CacheStore:
    def __init__(self) -> None:
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.prefix = os.getenv("CACHE_PREFIX", "aletheia")
        self._client = None
        if self.enabled and redis is not None:
            try:
                self._client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                self._client.ping()
            except Exception:
                self._client = None

    def is_ready(self) -> bool:
        if not self.enabled:
            return True
        if not self._client:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def make_key(self, namespace: str, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{self.prefix}:{namespace}:{digest}"

    def get(self, key: str) -> dict[str, Any] | None:
        if not self._client:
            return None
        try:
            data = self._client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        if not self._client:
            return
        try:
            self._client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
        except Exception:
            pass

    def clear_namespace(self, namespace: str) -> int:
        if not self._client:
            return 0
        pattern = f"{self.prefix}:{namespace}:*"
        deleted = 0
        try:
            cursor = 0
            while True:
                cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=200)
                if keys:
                    deleted += int(self._client.delete(*keys))
                if cursor == 0:
                    break
        except Exception:
            return deleted
        return deleted

    def clear_all(self) -> int:
        total = 0
        total += self.clear_namespace("search")
        total += self.clear_namespace("ask")
        return total
