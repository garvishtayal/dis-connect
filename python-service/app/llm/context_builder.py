from typing import Any, Sequence

from app.models.content import ContentItem


# Builds a simple context string from ContentItems (e.g. for rank prompt).
def build_content_context(items: Sequence[ContentItem]) -> str:
    titles = [item.title for item in items]
    return " | ".join(titles)


# Builds a short summary of raw item dicts for the rank LLM prompt.
def build_raw_items_summary(raw_items: Sequence[dict[str, Any]]) -> str:
    lines = []
    for i, r in enumerate(raw_items):
        lines.append(f"{i}: {r.get('title', '')} | {r.get('url', '')} | {r.get('platform', '')}")
    return "\n".join(lines) if lines else "(no items)"

