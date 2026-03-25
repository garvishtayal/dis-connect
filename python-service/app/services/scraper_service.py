"""Thin scraper service — no business logic. Each function is called directly by Go workers via HTTP."""
from app.models.content import ContentItem
from app.scrapers import pinterest, youtube
from app.scrapers.models import PinRawItem, YtRawItem


def _raw_to_item(raw: dict) -> ContentItem:
    return ContentItem(
        id=str(raw.get("id", "")),
        type=str(raw.get("type", "image")),
        platform=str(raw.get("platform", "")),
        url=str(raw.get("url", "")),
        title=str(raw.get("title", "")),
        score=0.0,
        metadata=raw.get("metadata"),
    )


async def scrape_youtube(query: str) -> list[ContentItem]:
    raw_items = await youtube.search(query)
    return [_raw_to_item(r) for r in raw_items]


async def scrape_pinterest(query: str, proxy: str = "") -> list[ContentItem]:
    raw_items = await pinterest.search(query, proxy=proxy)
    return [_raw_to_item(r) for r in raw_items]
