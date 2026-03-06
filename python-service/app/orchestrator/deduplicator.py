from app.models.content import ContentItem


# Deduplicates content items by URL while preserving order.
def deduplicate(items: list[ContentItem]) -> list[ContentItem]:
    seen: set[str] = set()
    result: list[ContentItem] = []
    for item in items:
        if item.url in seen:
            continue
        seen.add(item.url)
        result.append(item)
    return result

