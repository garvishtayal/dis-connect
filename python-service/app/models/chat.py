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
class ChatResponse(BaseModel):
    chat_response: str
    needs_new_content: bool


# Request body for /preferences – updates content preferences via LLM.
class PreferencesRequest(BaseModel):
    user_id: str
    preferences: dict[str, Any] | None = None
    recent_chats: list[Any] | None = None


# Response body for /preferences – returns updated preferences object.
class PreferencesResponse(BaseModel):
    preferences: dict[str, Any]
