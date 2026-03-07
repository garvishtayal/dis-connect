from typing import Any

import redis.asyncio as aioredis

from app.config import REDIS_URL

# Key patterns (match product-notes/redis.txt).
KEY_SHOWN = "user:{user_id}:shown"
KEY_PREFERENCES = "user:{user_id}:preferences"
TTL_SHOWN_DAYS = 7
TTL_PREFERENCES_DAYS = 30


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
