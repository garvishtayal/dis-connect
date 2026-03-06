from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.chat import (
    ChatRequest,
    ChatResponse,
    GenerateQueriesRequest,
    GenerateQueriesResponse,
    Query,
    RankRequest,
    RankResponse,
    UnderstandSoulRequest,
    UnderstandSoulResponse,
)
from app.models.content import ContentItem
from app.services import agent_service, orchestrator_service

router = APIRouter()


# Simple health check endpoint for the agent service.
@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Understands a user's initial soul prompt using the agent service.
@router.post("/agent/understand-soul", response_model=UnderstandSoulResponse)
async def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    return agent_service.understand_soul(req)


# Generates platform search queries from the user's goal and profile.
@router.post("/agent/generate-queries", response_model=GenerateQueriesResponse)
async def generate_queries(req: GenerateQueriesRequest) -> GenerateQueriesResponse:
    return agent_service.generate_queries(req)


# Ranks raw content results using the agent service.
@router.post("/agent/rank", response_model=RankResponse)
async def rank(req: RankRequest) -> RankResponse:
    return agent_service.rank(req)


# Handles chat messages and hints whether new content should be fetched.
@router.post("/agent/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    return agent_service.chat(req)


class FetchContentRequest(BaseModel):
    user_id: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    recent_chats: list[Any] | None = None
    queries: list[Query] | None = None


class FetchContentResponse(BaseModel):
    items: list[ContentItem]


# Fetches content items for the orchestrator using the placeholder pipeline.
@router.post("/orchestrator/fetch-content", response_model=FetchContentResponse)
async def fetch_content(req: FetchContentRequest) -> FetchContentResponse:
    items = await orchestrator_service.fetch_content(
        user_id=req.user_id,
        user_goal=req.user_goal,
        user_profile=req.user_profile,
        recent_chats=req.recent_chats,
        queries=req.queries,
    )
    return FetchContentResponse(items=items)

