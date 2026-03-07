from typing import Any

from app.models.content import ContentItem


# Deduplicates by URL in memory (preserves order).
def deduplicate(items: list[ContentItem]) -> list[ContentItem]:
    seen: set[str] = set()
    result: list[ContentItem] = []
    for item in items:
        if item.url in seen:
            continue
        seen.add(item.url)
        result.append(item)
    return result


# Filters out raw items whose url is in the already-shown set (Redis).
def filter_already_shown_raw(raw: list[dict[str, Any]], shown_urls: set[str]) -> list[dict[str, Any]]:
    return [r for r in raw if r.get("url") not in shown_urls]

