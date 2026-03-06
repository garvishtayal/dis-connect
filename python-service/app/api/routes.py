from typing import Any

from fastapi import APIRouter

from app.llm.client import LLMClient
from app.llm.prompts import build_goal_prompt
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
from app.orchestrator.orchestrator import fetch_content as orchestrator_fetch_content

router = APIRouter()
llm_client = LLMClient()


# Simple health check endpoint for the agent service.
@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


# Understands a user's initial soul prompt using trivial echo logic.
@router.post("/agent/understand-soul", response_model=UnderstandSoulResponse)
async def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    soul = req.initial_prompt.strip()
    return UnderstandSoulResponse(user_id=req.user_id, soul=soul)


# Generates platform search queries from the user's goal and profile.
@router.post("/agent/generate-queries", response_model=GenerateQueriesResponse)
async def generate_queries(req: GenerateQueriesRequest) -> GenerateQueriesResponse:
    goal = req.user_goal.strip() if req.user_goal else "career growth"
    queries = [
        Query(platform="youtube", query=goal),
        Query(platform="pinterest", query=goal),
        Query(platform="reddit", query=goal),
    ]
    return GenerateQueriesResponse(queries=queries)


# Ranks raw content results with simple score-based logic and notes.
@router.post("/agent/rank", response_model=RankResponse)
async def rank(req: RankRequest) -> RankResponse:
    items: list[ContentItem] = []
    for index, raw in enumerate(req.raw_results):
        item = raw if isinstance(raw, dict) else {}
        items.append(
            ContentItem(
                id=str(item.get("id", f"item-{index+1}")),
                type=str(item.get("type", "unknown")),
                platform=str(item.get("platform", "unknown")),
                url=str(item.get("url", "")),
                title=str(item.get("title", "")),
                manifestation_note=str(
                    item.get("manifestation_note", "Aligned with your goal.")
                ),
                score=float(item.get("score", 0.5)),
            )
        )
    ranked_items = sorted(items, key=lambda x: x.score, reverse=True)
    return RankResponse(items=ranked_items)


# Handles chat messages and hints whether new content should be fetched.
@router.post("/agent/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    prompt = build_goal_prompt(req.user_goal, req.user_profile)
    _ = llm_client.generate_text(prompt)
    return ChatResponse(
        chat_response="Got it. I can fetch content aligned with your goal.",
        needs_new_content=True,
        search_queries=None,
        manifestation_tip=None,
    )


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
    queries = req.queries or []
    items = await orchestrator_fetch_content(queries)
    return FetchContentResponse(items=items)

