from typing import Any

from app.models.chat import Query


# Generates queries in ratio from initial_prompt + enhanced_profile + preferences + recent_chats (placeholder).
def generate_queries_ratio(
    initial_prompt: str,
    enhanced_profile: str,
    preferences: dict[str, Any] | None,
    recent_chats: list[Any] | None,
) -> list[Query]:
    goal = f"{initial_prompt or ''} {enhanced_profile or ''}".strip() or "career growth"
    queries: list[Query] = []
    for i in range(4):
        queries.append(Query(platform="pinterest", query=goal, content_type="image"))
    for i in range(3):
        queries.append(Query(platform="instagram", query=goal, content_type="image"))
    for i in range(3):
        queries.append(Query(platform="instagram", query=goal, content_type="short"))
    for i in range(3):
        queries.append(Query(platform="youtube", query=goal, content_type="short"))
    for i in range(3):
        queries.append(Query(platform="youtube", query=goal, content_type="video"))
    return queries
