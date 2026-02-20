import time
from pathlib import Path

# TTL in seconds (5 minutes)
CACHE_TTL = 300


class CacheEntry:
    """Single cached item with TTL and mtime tracking."""
    def __init__(self, data, file_path: Path | None = None):
        self.data = data
        self.file_path = file_path
        self.cached_at = time.time()
        self.cached_mtime = file_path.stat().st_mtime if file_path and file_path.exists() else None

    def is_valid(self) -> bool:
        """Check if cache is still fresh (TTL or mtime-based invalidation)."""
        # Check TTL
        if time.time() - self.cached_at > CACHE_TTL:
            return False
        # Check mtime if we have a file
        if self.file_path and self.file_path.exists():
            current_mtime = self.file_path.stat().st_mtime
            if current_mtime != self.cached_mtime:
                return False
        return True


class Cache:
    """Simple in-memory cache for data loaders."""
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}

    def get(self, key: str):
        """Get cached value if valid, else None."""
        entry = self._cache.get(key)
        if entry and entry.is_valid():
            return entry.data
        # Remove expired entry
        if key in self._cache:
            del self._cache[key]
        return None

    def set(self, key: str, data, file_path: Path | None = None):
        """Store value in cache."""
        self._cache[key] = CacheEntry(data, file_path)

    def invalidate(self, key: str | None = None):
        """Invalidate one key or entire cache."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()


# Global cache instance
_cache = Cache()


def get_cache() -> Cache:
    return _cache
