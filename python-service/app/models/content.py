from pydantic import BaseModel


# Represents a single normalized content item for the manifestation feed.
class ContentItem(BaseModel):
    id: str
    type: str
    platform: str
    url: str
    title: str
    manifestation_note: str
    score: float

