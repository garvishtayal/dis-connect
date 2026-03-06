from typing import Sequence

from app.models.content import ContentItem


# Builds a simple context string from a sequence of content items.
def build_content_context(items: Sequence[ContentItem]) -> str:
    titles = [item.title for item in items]
    return " | ".join(titles)

