from typing import Any

from pydantic import BaseModel


# Single content item; matches Go models.ContentItem (id, type, platform, url, title, score, metadata).
class ContentItem(BaseModel):
    id: str
    type: str
    platform: str
    url: str
    title: str
    score: float = 0.0
    metadata: dict[str, Any] | None = None


# Response body for /agent/generate-content (items relaxed to Any for testing raw_per_query).
class GenerateContentResponse(BaseModel):
    items: list[Any]
