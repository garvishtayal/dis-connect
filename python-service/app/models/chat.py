from typing import Any

from pydantic import BaseModel


# Represents the request body for understanding a user's initial soul prompt.
class UnderstandSoulRequest(BaseModel):
    user_id: str
    initial_prompt: str


# Represents the response after understanding a user's soul prompt.
class UnderstandSoulResponse(BaseModel):
    user_id: str
    soul: str


# Represents a single search query for a specific content platform.
class Query(BaseModel):
    platform: str
    query: str


# Represents the request body for generating search queries.
class GenerateQueriesRequest(BaseModel):
    user_id: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    recent_chats: list[Any] | None = None


# Represents the response body containing generated search queries.
class GenerateQueriesResponse(BaseModel):
    queries: list[Query]


# Represents the request body for ranking raw content results.
class RankRequest(BaseModel):
    user_id: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    raw_results: list[dict[str, Any] | Any]


# Represents one ranked content item returned from the agent.
class RankedItem(BaseModel):
    id: str
    type: str
    platform: str
    url: str
    title: str
    manifestation_note: str
    score: float


# Represents the response body containing ranked content items.
class RankResponse(BaseModel):
    items: list[RankedItem]


# Represents the request body for the chat agent endpoint.
class ChatRequest(BaseModel):
    user_id: str
    message: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    chat_history: list[Any] | None = None
    current_content_ids: list[str] | None = None


# Represents the response body for the chat agent endpoint.
class ChatResponse(BaseModel):
    chat_response: str
    needs_new_content: bool
    search_queries: list[Query] | None = None
    manifestation_tip: str | None = None

