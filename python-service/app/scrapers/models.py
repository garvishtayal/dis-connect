"""Platform-specific raw item models; all normalize to the same dict shape for pipeline (id, type, platform, url, title, metadata)."""
from typing import Any

from pydantic import BaseModel


# YouTube: one search result (short or video) before pipeline.
class YtRawItem(BaseModel):
    id: str
    type: str  # "short" | "video"
    platform: str = "youtube"
    url: str
    title: str
    metadata: dict[str, Any] = {}

    # Serializes to pipeline raw dict (id, type, platform, url, title, metadata).
    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


# Instagram: one post (photo or reel) before pipeline.
class IgRawItem(BaseModel):
    id: str
    type: str  # "image" | "short"
    platform: str = "instagram"
    url: str
    title: str
    metadata: dict[str, Any] = {}

    # Serializes to pipeline raw dict (id, type, platform, url, title, metadata).
    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


# Pinterest: one pin (image) before pipeline.
class PinRawItem(BaseModel):
    id: str
    type: str = "image"
    platform: str = "pinterest"
    url: str
    title: str
    metadata: dict[str, Any] = {}

    # Serializes to pipeline raw dict (id, type, platform, url, title, metadata).
    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
