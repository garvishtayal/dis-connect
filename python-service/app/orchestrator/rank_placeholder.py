from typing import Any

from app.models.content import ContentItem


# Placeholder rank: assigns score 0.8 to each raw item (no LLM call).
def rank_raw_items(raw: list[dict[str, Any]], _user_goal: str, _user_profile: dict[str, Any] | None) -> list[ContentItem]:
    items: list[ContentItem] = []
    for i, r in enumerate(raw):
        items.append(
            ContentItem(
                id=str(r.get("id", f"item-{i+1}")),
                type=str(r.get("type", "unknown")),
                platform=str(r.get("platform", "unknown")),
                url=str(r.get("url", "")),
                title=str(r.get("title", "")),
                score=0.8,
                metadata={"manifestation_note": "Placeholder rank."},
            )
        )
    return items
