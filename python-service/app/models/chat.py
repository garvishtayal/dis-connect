from typing import Any

from pydantic import BaseModel


# Request body for /agent/understand-soul (matches Go UnderstandSoulRequest).
class UnderstandSoulRequest(BaseModel):
    user_id: str
    initial_prompt: str
    recent_chats: list[Any] | None = None


# Response for /agent/understand-soul.
class UnderstandSoulResponse(BaseModel):
    user_id: str
    soul: str


# Request body for /agent/generate-content (matches Go GenerateContentRequest).
class GenerateContentRequest(BaseModel):
    user_id: str
    initial_prompt: str = ""
    enhanced_profile: str = ""
    preferences: dict[str, Any] | None = None
    recent_chats: list[Any] | None = None
    limit: int = 20


# Response for /agent/generate-content uses list[ContentItem] from content.py.


# Single search query; content_type used for ratio mix (image/short/video).
class Query(BaseModel):
    platform: str
    query: str
    content_type: str = "image"  # "image" | "short" | "video"


# Request body for /agent/chat (aligned with GenerateContentRequest-style context).
class ChatRequest(BaseModel):
    user_id: str
    message: str
    initial_prompt: str = ""
    enhanced_profile: str = ""
    preferences: dict[str, Any] | None = None
    recent_chats: list[Any] | None = None


# Response for /agent/chat.
# Matches Go ChatResponse: only chat_response and needs_new_content.
class ChatResponse(BaseModel):
    chat_response: str
    needs_new_content: bool
