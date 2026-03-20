"""Redis client and helpers. Dedup, preferences, search cache."""

from app.redis.client import (
    get_cached_queries,
    get_client,
    get_preferences,
    get_search_cached,
    get_shown_urls,
    set_cached_queries,
    set_search_cached,
)

__all__ = [
    "get_client",
    "get_shown_urls",
    "get_preferences",
    "get_search_cached",
    "set_search_cached",
    "get_cached_queries",
    "set_cached_queries",
]
