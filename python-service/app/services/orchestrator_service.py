from typing import Any

from app.models.chat import Query
from app.models.content import ContentItem
from app.orchestrator.orchestrator import fetch_content as orchestrator_fetch_content


# Handles orchestrator content fetching for the given request data.
async def fetch_content(
    user_id: str,
    user_goal: str,
    user_profile: dict[str, Any] | None,
    recent_chats: list[Any] | None,
    queries: list[Query] | None,
) -> list[ContentItem]:
    _ = (user_id, user_goal, user_profile, recent_chats)
    effective_queries = queries or []
    items = await orchestrator_fetch_content(effective_queries)
    return items

