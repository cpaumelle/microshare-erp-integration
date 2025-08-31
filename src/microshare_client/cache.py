"""
Simple in-memory cache for Microshare cluster data
TTL-based caching with automatic cleanup
"""
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CacheEntry:
    data: Any
    timestamp: float
    ttl: int

    @property
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry and not entry.is_expired:
            return entry.data
        elif entry:
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        self._cache[key] = CacheEntry(data=value, timestamp=time.time(), ttl=ttl)

    def delete(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    def cleanup_expired(self) -> int:
        expired_keys = [k for k, v in self._cache.items() if v.is_expired]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

# Global cache instance
cluster_cache = SimpleCache()
