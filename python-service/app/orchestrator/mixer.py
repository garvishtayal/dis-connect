from typing import Sequence

from app.models.content import ContentItem


# Performs a simple score-based sort of content items.
def mix(items: Sequence[ContentItem]) -> list[ContentItem]:
    return sorted(items, key=lambda item: item.score, reverse=True)

