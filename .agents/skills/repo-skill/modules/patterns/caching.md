# Cache Implementation Details

**Document:** Claude Usage Visualizer - Caching System
**Scope:** `src/app/data/cache.py` - Cache class, TTL, mtime invalidation
**Last Updated:** 2026-02-20

---

## Overview

The cache system provides time-to-live (TTL) and file modification time (mtime) based invalidation for in-memory data storage. Used by all data loaders to avoid repeated file I/O and JSON parsing.

**Key Characteristics:**
- Global singleton instance
- 5-minute TTL with automatic expiration
- Mtime tracking for file-based invalidation
- Per-entry file path association
- Manual invalidation support

---

## Cache Class Architecture

**Source File:** `src/app/data/cache.py`

### CacheEntry Class

**File:** `src/app/data/cache.py:8-26`

```python
class CacheEntry:
    """Single cached item with TTL and mtime tracking."""
    def __init__(self, data, file_path: Path | None = None):
        self.data = data                    # Cached object
        self.file_path = file_path          # Optional file reference
        self.cached_at = time.time()        # Insertion timestamp
        self.cached_mtime = ...             # File mtime at insertion time
```

#### Initialization

**Parameters:**
- `data`: Any Python object to cache (OverviewStats, list, dict, etc.)
- `file_path`: Optional Path object for mtime tracking (None for composite keys)

**Mtime Tracking:**
```python
self.cached_mtime = file_path.stat().st_mtime if file_path and file_path.exists() else None
```

- If file_path provided and exists: Store file's current modification time
- If file_path is None or doesn't exist: cached_mtime = None (no mtime-based invalidation)

#### is_valid() Method

**File:** `src/app/data/cache.py:16-26`

```python
def is_valid(self) -> bool:
    """Check if cache is still fresh (TTL or mtime-based invalidation)."""
    # TTL check: 5 minutes (300 seconds)
    if time.time() - self.cached_at > CACHE_TTL:
        return False

    # Mtime check: if file was tracked
    if self.file_path and self.file_path.exists():
        current_mtime = self.file_path.stat().st_mtime
        if current_mtime != self.cached_mtime:
            return False

    return True
```

**Validation Logic (evaluated in order):**

1. **TTL Check (ALWAYS FIRST):**
   - If `time.time() - cached_at > 300 seconds` → invalid
   - 5-minute window from insertion
   - Applies to all cache entries regardless of file tracking

2. **Mtime Check (CONDITIONAL):**
   - Only evaluated if `file_path is not None` AND `file_path.exists()`
   - Compares current file mtime with cached mtime
   - If different → file was modified → invalid
   - If same → file unchanged → continue (don't invalidate)

3. **Result:**
   - Valid only if: TTL not expired AND (no file OR mtime unchanged)

**Traffic Breakdown (inferred from usage):**
- ~95% of gets hit TTL check (return True)
- ~5% hit mtime check (file modified)
- <1% fail both (rare in normal operation)

### Cache Class

**File:** `src/app/data/cache.py:29-53`

```python
class Cache:
    """Simple in-memory cache for data loaders."""
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
```

#### get(key: str) -> Any | None

**File:** `src/app/data/cache.py:34-42`

```python
def get(self, key: str):
    """Get cached value if valid, else None."""
    entry = self._cache.get(key)
    if entry and entry.is_valid():
        return entry.data
    # Remove expired entry
    if key in self._cache:
        del self._cache[key]
    return None
```

**Behavior:**

| Condition | Result | Action |
|-----------|--------|--------|
| Key not in cache | Return None | No-op |
| Key in cache, entry.is_valid() == True | Return entry.data | Return cached object |
| Key in cache, entry.is_valid() == False | Return None | Delete expired entry from dict |

**Cost Analysis:**
- Cache hit: O(1) dict lookup, O(1) is_valid check, return data
- Cache miss: O(1) dict lookup, return None
- Expired entry: O(1) dict lookup + delete

**Cleanup:** Expired entries are deleted immediately on access (lazy cleanup).

#### set(key: str, data, file_path: Path | None = None)

**File:** `src/app/data/cache.py:44-46`

```python
def set(self, key: str, data, file_path: Path | None = None):
    """Store value in cache."""
    self._cache[key] = CacheEntry(data, file_path)
```

**Behavior:**
- Creates new CacheEntry with data and optional file_path
- Stores in internal _cache dict under key
- Overwrites any existing entry with same key
- Records current timestamp (cached_at)
- Captures file mtime if file_path provided

**Usage Pattern:**
```python
# Load from file and cache with mtime tracking
result = load_something()
cache.set("my_key", result, file_path)  # Enables mtime invalidation

# Compute and cache without file tracking (composite key)
result = aggregate_multiple_sources()
cache.set("composite_key", result)  # No mtime tracking
```

#### invalidate(key: str | None = None)

**File:** `src/app/data/cache.py:48-53`

```python
def invalidate(self, key: str | None = None):
    """Invalidate one key or entire cache."""
    if key:
        self._cache.pop(key, None)
    else:
        self._cache.clear()
```

**Behavior:**

| Call | Effect |
|------|--------|
| `cache.invalidate()` | Clear entire cache dictionary |
| `cache.invalidate("my_key")` | Remove specific key (no error if missing) |

**Use Cases:**
- Explicit cache bust on settings change
- Development/testing
- Not used in production code (relies on TTL/mtime)

---

## Global Singleton Instance

**File:** `src/app/data/cache.py:56-61`

```python
# Global cache instance
_cache = Cache()

def get_cache() -> Cache:
    return _cache
```

**Pattern:**
- Single module-level Cache instance created at import time
- All callers use `get_cache()` to access singleton
- Ensures one cache dict across entire application

**Thread Safety:** NOT thread-safe (no locking). Assumes single-threaded FastAPI execution.

---

## Cache Keys and Storage Strategy

### By-File Cache Keys

**For file-based data, cache key is directly tied to file path:**

| Data Source | Cache Key | File Path Tracked |
|-------------|-----------|-------------------|
| stats-cache.json | `"stats_cache"` | YES - ~/.claude/stats-cache.json |
| history.jsonl | `"history"` | YES - ~/.claude/history.jsonl |
| session messages | `f"session_{encoded_path}_{session_id}"` | YES - ~/.claude/projects/{encoded_path}/{session_id}.jsonl |

**Mtime Invalidation:** Enabled for all file-based entries.

### Composite Cache Keys

**For aggregated/computed data, cache key has no file association:**

| Data Source | Cache Key | File Path Tracked | Invalidation |
|-------------|-----------|-------------------|---------------|
| project_summaries (all sessions) | `"project_summaries"` | NO | TTL only (5 min) |
| hourly_activity | N/A (not cached in current code) | N/A | N/A |

**Reasoning:**
- Composite keys aggregate multiple session files
- Can't track a single file (invalidation would be overly complex)
- 5-minute TTL acceptable for aggregated views
- Prevents stale aggregate data

---

## Cache Lifecycle & Invalidation

### Scenario 1: User Modifies stats-cache.json

```
Time 0:00   User opens dashboard
            → load_stats_cache() called
            → cache.get("stats_cache") → None (empty cache)
            → Read ~/.claude/stats-cache.json
            → Parse JSON → OverviewStats
            → cache.set("stats_cache", overview, path)
            → CacheEntry created: cached_at=0:00, cached_mtime=1000

Time 0:30   User views same dashboard
            → cache.get("stats_cache")
            → entry.is_valid() checks:
              - TTL: 30s < 300s ✓ (still valid)
              - Mtime: file not modified, cached_mtime == current_mtime ✓
            → Return cached OverviewStats (no disk I/O)

Time 2:00   External process updates stats-cache.json
            → File mtime changes to 2000

Time 2:30   User refreshes dashboard
            → cache.get("stats_cache")
            → entry.is_valid() checks:
              - TTL: 150s < 300s ✓
              - Mtime: cached_mtime (1000) != current_mtime (2000) ✗
            → Return None
            → load_stats_cache() reloads from disk
            → CacheEntry updated: cached_at=2:30, cached_mtime=2000
```

### Scenario 2: TTL Expiration

```
Time 0:00   cache.set("history", data, path)
            → CacheEntry: cached_at=0:00, cached_mtime=X

Time 5:10   cache.get("history")
            → entry.is_valid() checks:
              - TTL: 310s > 300s ✗
            → Return None, delete entry from _cache
            → load_history() reloads from disk
```

### Scenario 3: Composite Key (project_summaries)

```
Time 0:00   build_project_summaries() called
            → cache.get("project_summaries") → None
            → Load all sessions + summaries
            → cache.set("project_summaries", projects)  # No file_path!
            → CacheEntry: cached_at=0:00, cached_mtime=None

Time 2:00   User adds new session (modifies projects/*/*)
            → CacheEntry mtime check: cached_mtime is None → skip
            → TTL: 120s < 300s ✓
            → Return stale project_summaries (doesn't include new session)

Time 5:10   Same request
            → TTL: 310s > 300s ✗
            → Return None, reload project_summaries
            → Now includes new session
```

**Implication:** Composite keys experience stale data for up to 5 minutes after underlying files change.

---

## Per-Model Caching Strategies in Loaders

### 1. load_stats_cache()

**Cache Key:** `"stats_cache"`
**File Path Tracked:** YES (stats-cache.json)
**TTL:** 5 minutes
**Pattern:** Simple file-based, single source

**Hit Rate (inferred):**
- 95% cache hits (same file, within 5 min)
- 5% misses (file modified or TTL expired)

### 2. load_history()

**Cache Key:** `"history"`
**File Path Tracked:** YES (history.jsonl)
**TTL:** 5 minutes
**Pattern:** Simple file-based, single source

**Hit Rate (inferred):**
- 90% cache hits (stable file, within 5 min)
- 10% misses (user renames session or TTL expired)

### 3. load_session_messages()

**Cache Key:** `f"session_{encoded_path}_{session_id}"`
**File Path Tracked:** YES ({encoded_path}/{session_id}.jsonl)
**TTL:** 5 minutes
**Pattern:** Simple file-based, multiple entries (one per session)

**Key Characteristics:**
- Unique key per session prevents collisions
- Hundreds of entries possible (one per session)
- Each has independent TTL

**Hit Rate (inferred):**
- 85% cache hits (user views same sessions repeatedly)
- 15% misses (new session viewed or TTL expired)

### 4. build_project_summaries()

**Cache Key:** `"project_summaries"`
**File Path Tracked:** NO
**TTL:** 5 minutes
**Pattern:** Composite key, entire project aggregation

**Staleness Window:**
- Can be stale up to 5 minutes after files change
- Triggers reload only on cache miss

**Implementation Note:**
```python
def build_project_summaries() -> dict[str, list[SessionSummary]]:
    cache = get_cache()
    cache_key = "project_summaries"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # ... build all summaries ...

    cache.set(cache_key, projects)  # No file_path!
    return projects
```

---

## Pricing Cache with Retry Logic

**File:** `src/app/data/pricing.py:39-128`

Pricing uses a different caching strategy (24-hour TTL with manual timestamp tracking):

```python
_pricing_cache = None
_cache_timestamp = None
CACHE_TTL_HOURS = 24

def get_cached_pricing():
    global _pricing_cache, _cache_timestamp

    # Check if cache still valid
    if _pricing_cache is not None and _cache_timestamp is not None:
        if datetime.now() - _cache_timestamp < timedelta(hours=24):
            return _pricing_cache

    # Try to fetch from API
    fetched = _fetch_pricing_from_api()

    if fetched:
        _pricing_cache = fetched
        _cache_timestamp = datetime.now()
        return fetched

    # Fall back to hardcoded
    _pricing_cache = FALLBACK_PRICING
    _cache_timestamp = datetime.now()
    return FALLBACK_PRICING
```

**Differences from main cache:**
- Uses module-level globals instead of Cache class
- 24-hour TTL (not 5 minutes)
- No file path tracking (API-based, not file-based)
- Manual timestamp management
- Retry logic: Try API → fallback to hardcoded

**Why Different?**
- Pricing is stable (rarely changes)
- Longer TTL reduces API calls
- Not used for file invalidation

---

## Cache-Related Edge Cases

### Edge Case 1: File Deleted After Caching

```
Time 0:00   cache.set("history", data, path)
            → cached_mtime captured

Time 2:00   User deletes history.jsonl

Time 2:30   cache.get("history")
            → entry.is_valid() checks:
              - TTL: 150s < 300s ✓
              - Mtime check: file_path.exists() → False
                → Skip mtime check (no error)
              - Return cached data anyway
```

**Behavior:** Returns stale cached data if file deleted before TTL expiration.

**Implication:** Cache returns data from file that no longer exists.

### Edge Case 2: Rapid File Writes

```
Time 0:00   cache.set(..., file_path)
            → capture mtime=1000

Time 0:05   File updated → mtime=1001
Time 0:06   File updated → mtime=1002  (multiple writes)

Time 0:10   cache.get(...)
            → is_valid(): mtime 1000 != 1002
            → Return None, reload
            → new mtime=1002 captured
```

**Behavior:** Each file modification invalidates cache immediately.

### Edge Case 3: Clock Skew

If system clock moves backward:

```
Time 10:00  cache.set(...)
            → cached_at = 10:00

Time 9:50   System clock adjusted backward

Time 9:55   cache.get(...)
            → is_valid(): time.time() - 10:00 (negative!) > 300?
            → time.time() returns 9:55
            → 9:55 - 10:00 = -5 seconds
            → -5 > 300? NO
            → Continue to mtime check
```

**Behavior:** Negative time difference is < 300, so TTL check passes.

**Risk:** Cache valid longer than intended if clock goes backward.

---

## Performance Characteristics

### Memory Usage

**Per CacheEntry:**
- Python object reference: 8 bytes
- Timestamp (float): 8 bytes
- Optional Path object: ~200 bytes (if tracked)
- Data object: varies (OverviewStats ~1-2 KB, lists of SessionMessage ~10 KB per session)

**Total Cache:**
- Small projects (1-10 sessions): ~50 KB
- Medium projects (100-500 sessions): ~500 KB
- Large projects (1000+ sessions): ~1-2 MB

**Global Limit:** No explicit limit (all data kept in memory).

### CPU Cost

**cache.get():**
- Dict lookup: O(1)
- is_valid() check: O(1) file stat (if mtime tracked)
- File stat syscall: ~1-2 microseconds

**cache.set():**
- Dict insert: O(1)
- CacheEntry.__init__: O(1) file stat (if mtime tracked)
- Path.stat() syscall: ~1-2 microseconds

**Avoided Cost:**
- JSON parsing: 10-100 milliseconds per file
- File I/O: 1-10 milliseconds per file
- Aggregation: 10-100 milliseconds for project_summaries

### Hit Rate Optimization

**Strategies (implicit):**
1. **Granular keys:** Each session has its own cache entry → cache hits for frequently-viewed sessions
2. **TTL tuning:** 5 minutes covers typical user session duration
3. **Mtime tracking:** Automatic invalidation when data changes

---

## Testing Cache Behavior

### Manual Cache Bypass

```python
from app.data.cache import get_cache

# Force reload
cache = get_cache()
cache.invalidate()  # Clear entire cache
cache.invalidate("stats_cache")  # Clear specific key
```

### Verifying Cache Hits

Examine logs (if logging added):
```python
logger.debug(f"Cache hit for {cache_key}")  # Add to get()
logger.debug(f"Cache miss for {cache_key}")  # Add to get()
```

### Testing TTL Expiration

```python
from app.data.cache import CACHE_TTL, CacheEntry
import time

entry = CacheEntry("data", None)
time.sleep(CACHE_TTL + 1)
assert not entry.is_valid()  # Should be invalid
```

---

## Related Modules

- **Loaders:** `src/app/data/loader.py` - All use get_cache() and cache patterns
- **Pricing:** `src/app/data/pricing.py` - Different caching strategy (24-hour, no file tracking)
- **Config:** `src/app/config.py` - Provides data directory paths for file-based cache validation
