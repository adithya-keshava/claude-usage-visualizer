import logging
import re
from datetime import datetime, timedelta
from html.parser import HTMLParser

logger = logging.getLogger(__name__)

# Pricing docs URL – source of truth for live pricing
PRICING_DOCS_URL = "https://platform.claude.com/docs/en/about-claude/pricing"

# Fallback pricing: $/MTok (million tokens), keyed by normalized model pattern.
# Patterns are derived from display names: "Claude Opus 4.6" -> "opus-4-6".
# These values match the docs page as of 2026-03-12.
FALLBACK_PRICING = {
    "opus-4-6": {
        "input": 5.00,
        "output": 25.00,
        "cache_write": 6.25,
        "cache_read": 0.50,
    },
    "opus-4-5": {
        "input": 5.00,
        "output": 25.00,
        "cache_write": 6.25,
        "cache_read": 0.50,
    },
    "opus-4-1": {
        "input": 15.00,
        "output": 75.00,
        "cache_write": 18.75,
        "cache_read": 1.50,
    },
    "opus-4": {
        "input": 15.00,
        "output": 75.00,
        "cache_write": 18.75,
        "cache_read": 1.50,
    },
    "sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    "sonnet-4-5": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    "sonnet-4": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    "haiku-4-6": {
        "input": 1.00,
        "output": 5.00,
        "cache_write": 1.25,
        "cache_read": 0.10,
    },
    "haiku-4-5": {
        "input": 1.00,
        "output": 5.00,
        "cache_write": 1.25,
        "cache_read": 0.10,
    },
    "haiku-3-5": {
        "input": 0.80,
        "output": 4.00,
        "cache_write": 1.00,
        "cache_read": 0.08,
    },
    "haiku-3": {
        "input": 0.25,
        "output": 1.25,
        "cache_write": 0.30,
        "cache_read": 0.03,
    },
    "opus-3": {
        "input": 15.00,
        "output": 75.00,
        "cache_write": 18.75,
        "cache_read": 1.50,
    },
}

# Fallback for completely unknown models (use Sonnet 4.5 rates)
DEFAULT_PRICING = FALLBACK_PRICING["sonnet-4-5"]

# Module-level cache
_pricing_cache: dict | None = None
_cache_timestamp: datetime | None = None
_using_fallback: bool = False
CACHE_TTL_HOURS = 24


def _normalize_display_name(display_name: str) -> str:
    """
    Convert a pricing-page display name to a normalized pattern key.

    Examples:
        "Claude Opus 4.6" -> "opus-4-6"
        "Claude Haiku 3.5" -> "haiku-3-5"
        "Claude Sonnet 3.7 (deprecated)" -> "sonnet-3-7"
    """
    name = display_name.lower().strip()
    # Strip parenthetical annotations like "(deprecated)"
    name = re.sub(r"\s*\([^)]*\)", "", name)
    # Strip leading "claude "
    name = re.sub(r"^claude\s+", "", name)
    # Collapse whitespace to hyphens, replace dots with hyphens
    name = name.strip().replace(" ", "-").replace(".", "-")
    return name


def _match_model_to_pattern(model_id: str, pricing_by_pattern: dict) -> dict | None:
    """
    Match a model ID such as 'claude-opus-4-5-20251101' to a pricing pattern.

    Algorithm:
    1. Strip the leading 'claude-' prefix from the model ID.
    2. Check each pattern (sorted longest-first so more-specific wins) against
       the remaining string using exact equality or startswith(pattern + '-').

    Examples:
        "claude-opus-4-6"          matches "opus-4-6"  (exact)
        "claude-opus-4-5-20251101" matches "opus-4-5"  (prefix + date)
        "claude-sonnet-4-5-20250929" matches "sonnet-4-5"
    """
    model_lower = model_id.lower()
    tail = model_lower[len("claude-"):] if model_lower.startswith("claude-") else model_lower

    # Longer patterns are more specific – check them first to avoid "opus-4"
    # incorrectly matching "opus-4-5-..." before "opus-4-5" can be checked.
    for pattern, price in sorted(pricing_by_pattern.items(), key=lambda x: len(x[0]), reverse=True):
        if tail == pattern or tail.startswith(pattern + "-"):
            return price
    return None


class _PricingTableParser(HTMLParser):
    """Extract rows from the first HTML <table> on the pricing page."""

    def __init__(self):
        super().__init__()
        self._in_first_table = False
        self._table_count = 0
        self._in_cell = False
        self.rows: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_cell: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._table_count += 1
            if self._table_count == 1:
                self._in_first_table = True
        elif self._in_first_table and tag in ("td", "th"):
            self._in_cell = True
            self._current_cell = []
        elif self._in_first_table and tag == "tr":
            self._current_row = []

    def handle_endtag(self, tag):
        if tag == "table" and self._in_first_table:
            self._in_first_table = False
        elif self._in_first_table and tag in ("td", "th"):
            self._in_cell = False
            self._current_row.append("".join(self._current_cell).strip())
        elif self._in_first_table and tag == "tr":
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = []

    def handle_data(self, data):
        if self._in_cell:
            self._current_cell.append(data)


def _fetch_pricing_from_docs() -> dict | None:
    """
    Fetch live pricing from Anthropic's pricing documentation page.

    Parses the first HTML table on the page which has columns:
      Model | Base Input | 5m Cache Writes | 1h Cache Writes | Cache Hits | Output

    Returns:
        Dict keyed by normalized pattern (e.g. "opus-4-6") with pricing sub-dicts,
        or None if the fetch or parse fails.
    """
    try:
        import requests

        response = requests.get(
            PRICING_DOCS_URL,
            timeout=10,
            headers={"User-Agent": "claude-usage-visualizer/1.0"},
        )
        response.raise_for_status()

        parser = _PricingTableParser()
        parser.feed(response.text)

        if not parser.rows:
            logger.warning("Pricing page: no HTML table found")
            return None

        def _parse_price(cell: str) -> float | None:
            m = re.search(r"\$([0-9]+(?:\.[0-9]+)?)", cell)
            return float(m.group(1)) if m else None

        pricing_data: dict = {}
        for row in parser.rows:
            if len(row) < 6:
                continue
            model_name = row[0]
            if model_name.lower() in ("model", ""):
                continue  # header row

            # Column layout: Model | Input | 5m Cache Write | 1h Cache Write | Cache Read | Output
            input_price = _parse_price(row[1])
            cache_write = _parse_price(row[2])   # 5-minute cache write
            cache_read = _parse_price(row[4])    # cache hits & refreshes
            output_price = _parse_price(row[5])

            if input_price is None or output_price is None:
                continue

            pattern = _normalize_display_name(model_name)
            pricing_data[pattern] = {
                "input": input_price,
                "output": output_price,
                "cache_write": cache_write if cache_write is not None else round(input_price * 1.25, 4),
                "cache_read": cache_read if cache_read is not None else round(input_price * 0.1, 4),
            }

        if pricing_data:
            logger.info("Fetched pricing for %d models from %s", len(pricing_data), PRICING_DOCS_URL)
            return pricing_data

        logger.warning("Pricing page: table parsed but no valid rows found")
        return None

    except Exception as exc:
        logger.warning("Failed to fetch pricing from docs page: %s. Using fallback.", exc)
        return None


def get_cached_pricing() -> dict:
    """
    Return pattern-keyed pricing dict, refreshing after TTL expiry.

    Tries the live docs page on first use or when the 24-hour TTL has elapsed.
    Falls back to FALLBACK_PRICING when the page is unreachable.
    """
    global _pricing_cache, _cache_timestamp, _using_fallback

    if _pricing_cache is not None and _cache_timestamp is not None:
        if datetime.now() - _cache_timestamp < timedelta(hours=CACHE_TTL_HOURS):
            return _pricing_cache

    fetched = _fetch_pricing_from_docs()
    if fetched:
        _pricing_cache = fetched
        _cache_timestamp = datetime.now()
        _using_fallback = False
        return _pricing_cache

    logger.debug("Using hardcoded fallback pricing")
    _pricing_cache = FALLBACK_PRICING
    _cache_timestamp = datetime.now()
    _using_fallback = True
    return FALLBACK_PRICING


def refresh_pricing_cache() -> dict:
    """
    Force-discard the cached pricing and fetch fresh data.

    Returns the newly loaded pricing dict (or fallback on failure).
    """
    global _pricing_cache, _cache_timestamp
    _pricing_cache = None
    _cache_timestamp = None
    logger.info("Pricing cache cleared – fetching fresh data")
    return get_cached_pricing()


def get_pricing_info() -> dict:
    """
    Return a summary of the current pricing cache state for the API.
    """
    return {
        "source": "fallback" if _using_fallback else "live",
        "url": PRICING_DOCS_URL,
        "models": len(_pricing_cache) if _pricing_cache else 0,
        "cache_timestamp": _cache_timestamp.isoformat() if _cache_timestamp else None,
        "ttl_hours": CACHE_TTL_HOURS,
    }


def get_model_pricing(model_id: str) -> dict:
    """
    Return pricing for a model, defaulting to Sonnet 4.5 rates if unknown.
    """
    pricing = get_cached_pricing()
    matched = _match_model_to_pattern(model_id, pricing)
    if matched:
        return matched
    logger.warning("Unknown model %s – using Sonnet 4.5 rates as fallback", model_id)
    return DEFAULT_PRICING


def estimate_cost(
    model_id: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
) -> float:
    """
    Estimate cost in USD for a message or session.

    Formula:
        cost = (input × input_rate
              + output × output_rate
              + cache_creation × cache_write_rate
              + cache_read × cache_read_rate) / 1_000_000
    """
    pricing = get_model_pricing(model_id)
    return (
        input_tokens * pricing["input"]
        + output_tokens * pricing["output"]
        + cache_creation_input_tokens * pricing["cache_write"]
        + cache_read_input_tokens * pricing["cache_read"]
    ) / 1_000_000
