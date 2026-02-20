import logging
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Hardcoded fallback pricing: $/MTok (million tokens)
# Used when API is unavailable or for testing
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

# Fallback for unknown models
DEFAULT_PRICING = FALLBACK_PRICING["claude-sonnet-4-5-20250929"]

# Cache pricing data with 24-hour TTL
_pricing_cache = None
_cache_timestamp = None
CACHE_TTL_HOURS = 24


def _fetch_pricing_from_api() -> dict[str, dict[str, float]] | None:
    """
    Fetch latest pricing from Anthropic's API.

    This function attempts to fetch real-time pricing from Anthropic's
    models API endpoint. If the API is unavailable or returns an error,
    it falls back to hardcoded pricing.

    Returns:
        Dictionary mapping model IDs to pricing dicts, or None if fetch fails
    """
    try:
        import requests

        # Anthropic models API endpoint (public, no auth required)
        url = "https://api.anthropic.com/models"

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        models = response.json().get("data", [])
        pricing_data = {}

        for model in models:
            model_id = model.get("id")
            display_name = model.get("display_name", "")

            # Extract pricing from model metadata
            if "pricing" in model:
                pricing = model["pricing"]
                pricing_data[model_id] = {
                    "input": float(pricing.get("input_price", 0)) * 1_000_000,  # Convert to $/MTok
                    "output": float(pricing.get("output_price", 0)) * 1_000_000,
                    "cache_write": float(pricing.get("cache_creation_input_price", pricing.get("input_price", 0))) * 1_000_000 * 1.25,
                    "cache_read": float(pricing.get("cache_read_input_price", pricing.get("input_price", 0))) * 1_000_000 * 0.1,
                }
                logger.debug(f"Fetched pricing for {model_id}")

        if pricing_data:
            logger.info(f"Successfully fetched pricing for {len(pricing_data)} models from Anthropic API")
            return pricing_data
        else:
            logger.warning("Anthropic API returned no pricing data")
            return None

    except ImportError:
        logger.debug("requests library not available, using fallback pricing")
        return None
    except Exception as e:
        logger.warning(f"Failed to fetch pricing from Anthropic API: {e}. Using fallback pricing.")
        return None


@lru_cache(maxsize=1)
def get_cached_pricing() -> dict[str, dict[str, float]]:
    """
    Get pricing with caching and fallback.

    Attempts to fetch pricing from Anthropic's API, falling back to
    hardcoded pricing if unavailable. Caches result for 24 hours.

    Returns:
        Dictionary of model IDs to pricing information
    """
    global _pricing_cache, _cache_timestamp

    # Check if cache is still valid
    if _pricing_cache is not None and _cache_timestamp is not None:
        if datetime.now() - _cache_timestamp < timedelta(hours=CACHE_TTL_HOURS):
            return _pricing_cache

    # Try to fetch fresh pricing
    fetched = _fetch_pricing_from_api()

    if fetched:
        _pricing_cache = fetched
        _cache_timestamp = datetime.now()
        return fetched

    # Fall back to hardcoded pricing
    logger.debug("Using fallback hardcoded pricing")
    _pricing_cache = FALLBACK_PRICING
    _cache_timestamp = datetime.now()
    return FALLBACK_PRICING


def get_model_pricing(model_id: str) -> dict[str, float]:
    """
    Get pricing for a model, falling back to Sonnet rates if unknown.

    Fetches from cached/API pricing first, then falls back to hardcoded values.

    Args:
        model_id: The Claude model identifier

    Returns:
        Dictionary with "input", "output", "cache_write", "cache_read" keys
    """
    pricing = get_cached_pricing()

    if model_id in pricing:
        return pricing[model_id]

    logger.warning(f"Unknown model {model_id}, using Sonnet 4.5 rates as fallback")
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
    cost = (
        input_tokens * pricing["input"]
        + output_tokens * pricing["output"]
        + cache_creation_input_tokens * pricing["cache_write"]
        + cache_read_input_tokens * pricing["cache_read"]
    ) / 1_000_000
    return cost
