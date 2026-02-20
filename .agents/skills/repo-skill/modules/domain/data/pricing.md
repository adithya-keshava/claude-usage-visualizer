# Pricing & Cost Calculation

## Overview

The pricing module provides two strategies for calculating message and session costs:

1. **Dynamic pricing** - Fetch latest rates from Anthropic API (recommended)
2. **Fallback pricing** - Use hardcoded rates when API unavailable (resilient)

Both strategies support four token types: regular input, regular output, cache creation (write), and cache read.

**File Reference:** `src/app/data/pricing.py`

## Pricing Data Structure

### Model Pricing Format

All pricing is stored as a dictionary mapping model IDs to pricing tiers:

```python
{
    "model_id": {
        "input": float,         # $/million tokens
        "output": float,        # $/million tokens
        "cache_write": float,   # $/million tokens (cache creation)
        "cache_read": float,    # $/million tokens (cache read)
    },
    ...
}
```

**Units:** All prices are in $/million tokens ($/MTok)

**Example:** Claude Sonnet 4.5

```python
"claude-sonnet-4-5-20250929": {
    "input": 3.00,              # $3 per million input tokens
    "output": 15.00,            # $15 per million output tokens
    "cache_write": 3.75,        # $3.75 per million cache write tokens
    "cache_read": 0.30,         # $0.30 per million cache read tokens
}
```

## Hardcoded Fallback Pricing

**Location:** `src/app/data/pricing.py:9-34`

Fallback pricing is hardcoded for four Claude models:

```python
FALLBACK_PRICING = {
    "claude-opus-4-6": {
        "input": 15.00,
        "output": 75.00,
        "cache_write": 18.75,
        "cache_read": 1.50,
    },
    "claude-opus-4-5-20251101": {
        "input": 15.00,
        "output": 75.00,
        "cache_write": 18.75,
        "cache_read": 1.50,
    },
    "claude-sonnet-4-5-20250929": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    "claude-haiku-4-5-20251001": {
        "input": 0.80,
        "output": 4.00,
        "cache_write": 1.00,
        "cache_read": 0.08,
    },
}
```

**Purpose:**
- Fallback when API unreachable
- Testing and development
- Offline operation

**Default pricing** for unknown models: Claude Sonnet 4.5 rates

## Dynamic Pricing from API

### Fetching Latest Prices

**Function:** `_fetch_pricing_from_api()` at `src/app/data/pricing.py:45-95`

Fetches real-time pricing from Anthropic's public API:

```python
def _fetch_pricing_from_api() -> dict[str, dict[str, float]] | None:
    try:
        import requests
        url = "https://api.anthropic.com/models"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        models = response.json().get("data", [])
        pricing_data = {}

        for model in models:
            model_id = model.get("id")
            if "pricing" in model:
                pricing = model["pricing"]
                pricing_data[model_id] = {
                    "input": float(pricing.get("input_price", 0)) * 1_000_000,
                    "output": float(pricing.get("output_price", 0)) * 1_000_000,
                    "cache_write": float(pricing.get("cache_creation_input_price", ...)) * 1_000_000 * 1.25,
                    "cache_read": float(pricing.get("cache_read_input_price", ...)) * 1_000_000 * 0.1,
                }

        if pricing_data:
            return pricing_data
        else:
            return None

    except ImportError:
        logger.debug("requests library not available")
        return None
    except Exception as e:
        logger.warning(f"Failed to fetch pricing: {e}. Using fallback.")
        return None
```

**API Details:**

- **Endpoint:** `https://api.anthropic.com/models`
- **Method:** GET
- **Auth:** None required (public endpoint)
- **Timeout:** 5 seconds
- **Response format:** JSON array of model objects with `pricing` field

**Price conversion:**

API returns prices as `$/token`, converts to `$/million tokens`:

```python
"input": float(pricing.get("input_price", 0)) * 1_000_000
```

**Cache rate calculation:**

- **Cache write:** Base input price × 1.25 (heuristic)
  - API may not provide explicit cache_creation_input_price
  - Approximation: 1.25× because cache writes have slight overhead

- **Cache read:** Base input price × 0.1 (heuristic)
  - API may not provide explicit cache_read_input_price
  - Approximation: 0.1× because cache reads are discounted

**Error handling:**

1. **requests library not installed:** Log debug message, return None
2. **Network unreachable:** Exception caught, log warning, return None
3. **API returns error:** `raise_for_status()` raises, caught, log warning, return None
4. **No models in response:** Return None (empty response)

### Cached Pricing with TTL

**Function:** `get_cached_pricing()` at `src/app/data/pricing.py:98-128`

Implements simple caching with 24-hour TTL:

```python
@lru_cache(maxsize=1)
def get_cached_pricing() -> dict[str, dict[str, float]]:
    global _pricing_cache, _cache_timestamp

    if _pricing_cache is not None and _cache_timestamp is not None:
        if datetime.now() - _cache_timestamp < timedelta(hours=CACHE_TTL_HOURS):
            return _pricing_cache

    fetched = _fetch_pricing_from_api()

    if fetched:
        _pricing_cache = fetched
        _cache_timestamp = datetime.now()
        return fetched

    logger.debug("Using fallback hardcoded pricing")
    _pricing_cache = FALLBACK_PRICING
    _cache_timestamp = datetime.now()
    return FALLBACK_PRICING
```

**Cache mechanism:**

- Global variables: `_pricing_cache`, `_cache_timestamp`
- TTL: 24 hours (see `src/app/data/pricing.py:42`)
- LRU cache: Python's `functools.lru_cache(maxsize=1)` for function result caching

**Flow:**

1. **First call:** Attempt API fetch
   - Success: Cache and return API prices
   - Failure: Fall back to hardcoded, cache and return

2. **Subsequent calls within 24h:** Return cached value (hit)

3. **After 24h TTL expiry:** Attempt API fetch again (cache miss)

**Performance:**

- Cache hit: <1ms (dict lookup)
- Cache miss: 100-500ms (network call + parsing)

## Model Price Lookup

**Function:** `get_model_pricing()` at `src/app/data/pricing.py:131-149`

```python
def get_model_pricing(model_id: str) -> dict[str, float]:
    pricing = get_cached_pricing()

    if model_id in pricing:
        return pricing[model_id]

    logger.warning(f"Unknown model {model_id}, using Sonnet 4.5 rates as fallback")
    return DEFAULT_PRICING
```

**Lookup order:**

1. Get cached pricing (dynamic or hardcoded)
2. Look up model_id in pricing dict
3. If not found: Log warning, return Sonnet 4.5 rates (DEFAULT_PRICING)

**Typical model IDs:**

- `claude-opus-4-6`
- `claude-opus-4-5-20251101`
- `claude-sonnet-4-5-20250929`
- `claude-haiku-4-5-20251001`

## Cost Calculation

### Estimate Cost Function

**Function:** `estimate_cost()` at `src/app/data/pricing.py:152-175`

```python
def estimate_cost(
    model_id: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
) -> float:
    pricing = get_model_pricing(model_id)
    cost = (
        input_tokens * pricing["input"]
        + output_tokens * pricing["output"]
        + cache_creation_input_tokens * pricing["cache_write"]
        + cache_read_input_tokens * pricing["cache_read"]
    ) / 1_000_000
    return cost
```

**Formula:**

```
cost_usd = (
    (input_tokens × input_rate)
    + (output_tokens × output_rate)
    + (cache_creation_tokens × cache_write_rate)
    + (cache_read_tokens × cache_read_rate)
) / 1,000,000
```

**Example calculation:**

For Claude Opus 4.6 with:
- input_tokens: 100
- output_tokens: 200
- cache_creation_input_tokens: 50
- cache_read_input_tokens: 200

```python
pricing = {
    "input": 15.00,
    "output": 75.00,
    "cache_write": 18.75,
    "cache_read": 1.50,
}

cost = (
    100 × 15.00 +
    200 × 75.00 +
    50 × 18.75 +
    200 × 1.50
) / 1_000_000

cost = (
    1500 +
    15000 +
    937.50 +
    300
) / 1_000_000

cost = 17737.50 / 1_000_000 = $0.017737
```

**Rounding:** Returned as float, rounded by caller as needed

**All token types are optional:** Default to 0 if not provided

### Usage in Loaders

**SessionMessage cost calculation:**

`src/app/data/loader.py:226`:
```python
cost = estimate_cost(model, **parsed_usage)
```

Called during message parsing, stores in SessionMessage.cost_usd

**SessionSummary cost calculation:**

`src/app/data/loader.py:271`:
```python
total_cost = sum(m.cost_usd for m in messages)
```

Sum of all message costs

**ProjectSummary aggregation:**

`src/app/routers/projects.py:48`:
```python
total_cost = sum(s.total_cost_usd for s in sessions)
```

Sum of all session costs

### Usage in Routers

**Overview dashboard cost:**

`src/app/routers/overview.py:31-40`:
```python
total_cost = sum(
    estimate_cost(
        model_id,
        input_tokens=stats.input_tokens,
        output_tokens=stats.output_tokens,
        cache_creation_input_tokens=stats.cache_creation_input_tokens,
        cache_read_input_tokens=stats.cache_read_input_tokens,
    )
    for model_id, stats in overview_stats.model_stats.items()
)
```

Recalculates costs from ModelStats for each model

**Daily cost chart:**

`src/app/routers/api.py:113`:
```python
cost = estimate_cost(model_id, input_tokens=tokens // 2, output_tokens=tokens // 2)
```

Approximates input/output split from daily token counts (50/50 assumption)

## Pricing Calculation Flows

### Flow 1: First Message Load (Cache Miss)

```
User loads session detail
  ↓
load_session_messages(encoded_path, session_id)
  ├─ Check session message cache (miss)
  │
  └─ For each message in JSONL:
     ├─ estimate_cost(model_id, tokens...)
     │  ├─ get_model_pricing(model_id)
     │  │  ├─ get_cached_pricing()
     │  │  │  ├─ Check cache timestamp (miss or expired)
     │  │  │  │
     │  │  │  └─ _fetch_pricing_from_api()
     │  │  │     ├─ Network request to api.anthropic.com/models
     │  │  │     ├─ Parse response, convert $/token to $/MTok
     │  │  │     ├─ Cache result (24h TTL)
     │  │  │     └─ Return {model_id: {...pricing...}, ...}
     │  │  │
     │  │  └─ Look up model_id in pricing dict
     │  │     └─ Return pricing tier or fallback
     │  │
     │  └─ Calculate: cost = (...) / 1_000_000
     │
     └─ Create SessionMessage with cost_usd

  └─ Cache all messages

  ↓
Return HTML with message table and costs
```

**Performance:** 500ms-1s (includes API fetch)

### Flow 2: Cached Pricing Lookup

```
User loads another session within 24h
  ↓
load_session_messages(...)
  ├─ For each message:
  │  └─ estimate_cost(model_id, tokens...)
  │     └─ get_model_pricing(model_id)
  │        └─ get_cached_pricing()
  │           ├─ Check timestamp (hit)
  │           └─ Return cached {model_id: {...}}
  │
  └─ Calculate costs

  ↓
Return HTML
```

**Performance:** <10ms (all cached)

### Flow 3: Fallback Pricing

```
_fetch_pricing_from_api() fails
  ↓
get_cached_pricing()
  ├─ API returned None
  │
  └─ Use FALLBACK_PRICING
     ├─ Cache it with current timestamp
     └─ Return hardcoded dict

  ↓
All subsequent lookups use fallback
```

**Performance:** <1ms

## Cost Aggregation Examples

### Session Cost Aggregation

**Input:** 3 messages with costs $0.012, $0.015, $0.008

**Process:**
```python
messages = [
    SessionMessage(..., cost_usd=0.012),
    SessionMessage(..., cost_usd=0.015),
    SessionMessage(..., cost_usd=0.008),
]

total_cost = sum(m.cost_usd for m in messages)
# = 0.012 + 0.015 + 0.008 = $0.035
```

**Output:** SessionSummary with total_cost_usd = 0.035

### Project Cost Aggregation

**Input:** 5 sessions with costs $0.035, $0.042, $0.015, $0.050, $0.025

**Process:**
```python
sessions = [
    SessionSummary(..., total_cost_usd=0.035),
    SessionSummary(..., total_cost_usd=0.042),
    SessionSummary(..., total_cost_usd=0.015),
    SessionSummary(..., total_cost_usd=0.050),
    SessionSummary(..., total_cost_usd=0.025),
]

total_cost = sum(s.total_cost_usd for s in sessions)
# = 0.035 + 0.042 + 0.015 + 0.050 + 0.025 = $0.167
```

**Output:** ProjectSummary with total_cost_usd = 0.167

## Cache Integration Points

**In SessionMessage loading:**

Cost calculated once during JSONL parsing, stored in object, never recalculated.

**In overview calculation:**

Cost recalculated from ModelStats on each request:

`src/app/routers/overview.py:31-40`

This ensures accuracy if pricing changes.

**In daily cost chart:**

Cost approximated using 50/50 input/output split from daily token counts.

This is an estimate since daily breakdown doesn't distinguish input vs output.

## Handling Unknown Models

If a session uses a model not in pricing data:

1. `get_model_pricing()` looks up model_id (miss)
2. Log warning: "Unknown model X, using Sonnet 4.5 rates"
3. Return DEFAULT_PRICING (Sonnet 4.5)
4. Calculate cost using Sonnet rates

**Impact:** Unknown models get estimated as Sonnet cost

**Typical scenario:** When new Claude model released before app updated

## Testing Pricing

To test fallback pricing (bypass API):

1. **Uninstall requests library:**
   ```bash
   pip uninstall requests
   ```

2. **Or set invalid API endpoint:**
   (Not directly supported, would require code change)

3. **Or let API timeout:**
   API timeout is 5 seconds, will fall back to hardcoded

**Development setup:**

Use hardcoded pricing for consistent testing across environments.