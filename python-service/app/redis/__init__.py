"""Redis client and helpers. Python uses Redis for: dedup (read shown URLs), preferences (read filter)."""

from app.redis.client import get_client, get_preferences, get_shown_urls

__all__ = ["get_client", "get_shown_urls", "get_preferences"]
