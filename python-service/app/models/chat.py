from typing import Any

from pydantic import BaseModel


# Request body for /agent/understand-soul.
class UnderstandSoulRequest(BaseModel):
    user_id: str
    initial_prompt: str


# Response for /agent/understand-soul.
class UnderstandSoulResponse(BaseModel):
    user_id: str
    soul: str


# Request body for /agent/generate-content.
class GenerateContentRequest(BaseModel):
    user_id: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    recent_chats: list[Any] | None = None
    current_content_ids: list[str] | None = None
    limit: int = 20


# Response for /agent/generate-content uses list[ContentItem] from content.py.


# Single search query (optional in ChatResponse).
class Query(BaseModel):
    platform: str
    query: str


# Request body for /agent/chat.
class ChatRequest(BaseModel):
    user_id: str
    message: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    chat_history: list[Any] | None = None
    current_content_ids: list[str] | None = None


# Response for /agent/chat.
class ChatResponse(BaseModel):
    chat_response: str
    needs_new_content: bool
    search_queries: list[Query] | None = None
