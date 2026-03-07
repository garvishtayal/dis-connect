import hashlib
import json
from typing import Any

import redis.asyncio as aioredis

from app.config import REDIS_URL

# Key patterns (match product-notes/redis.txt).
KEY_SHOWN = "user:{user_id}:shown"
KEY_PREFERENCES = "user:{user_id}:preferences"
KEY_SEARCH = "search:{query_hash}"
TTL_SHOWN_DAYS = 7
TTL_PREFERENCES_DAYS = 30
TTL_SEARCH_SECONDS = 3600  # 1 hour


def get_client() -> aioredis.Redis:
    """Returns a Redis client using REDIS_URL. New connection each call; use a pool in production if needed."""
    return aioredis.from_url(REDIS_URL, decode_responses=True)


async def get_shown_urls(user_id: str) -> set[str]:
    """Reads the set of already-shown content URLs for this user (for dedup). Go writes; Python reads."""
    try:
        client = get_client()
        try:
            key = KEY_SHOWN.replace("{user_id}", user_id)
            urls = await client.smembers(key)
            return set(urls) if urls else set()
        finally:
            await client.aclose()
    except Exception:
        return set()


async def get_preferences(user_id: str) -> dict[str, Any]:
    """Reads user preferences (e.g. content_filter). Go reads+writes; Python reads."""
    try:
        client = get_client()
        try:
            key = KEY_PREFERENCES.replace("{user_id}", user_id)
            data = await client.hgetall(key)
            return dict(data) if data else {}
        finally:
            await client.aclose()
    except Exception:
        return {}


def _search_hash(platform: str, query: str, content_type: str = "") -> str:
    """Returns a short hash for cache key search:{hash}; content_type disambiguates YouTube/Instagram."""
    raw = f"{platform}:{query}:{content_type}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


async def get_search_cached(platform: str, query: str, content_type: str = "") -> list[dict[str, Any]] | None:
    """Reads cached raw results for this query (and content_type when applicable). Returns None on miss or error."""
    try:
        client = get_client()
        try:
            key = KEY_SEARCH.replace("{query_hash}", _search_hash(platform, query, content_type))
            data = await client.get(key)
            if not data:
                return None
            return json.loads(data)
        finally:
            await client.aclose()
    except Exception:
        return None


async def set_search_cached(platform: str, query: str, results: list[dict[str, Any]], content_type: str = "") -> None:
    """Writes raw results to cache with TTL 1 hour; content_type included in key for YouTube/Instagram."""
    try:
        client = get_client()
        try:
            key = KEY_SEARCH.replace("{query_hash}", _search_hash(platform, query, content_type))
            await client.set(key, json.dumps(results), ex=TTL_SEARCH_SECONDS)
        finally:
            await client.aclose()
    except Exception:
        pass
