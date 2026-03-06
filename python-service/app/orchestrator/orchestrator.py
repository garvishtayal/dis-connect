from typing import Sequence

from app.models.chat import Query
from app.models.content import ContentItem
from app.orchestrator import mixer, deduplicator


# Fetches content items for the given queries using placeholder logic.
async def fetch_content(queries: Sequence[Query]) -> list[ContentItem]:
    items: list[ContentItem] = []
    for index, query in enumerate(queries):
        items.append(
            ContentItem(
                id=f"placeholder-{index+1}",
                type="image",
                platform=query.platform,
                url=f"https://example.com/{query.platform}/{index+1}",
                title=f"Placeholder content for {query.query}",
                manifestation_note="Placeholder manifestation note.",
                score=0.5,
            )
        )
    mixed = mixer.mix(items)
    return deduplicator.deduplicate(mixed)

