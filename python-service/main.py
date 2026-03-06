from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="dis-connect Python Agent")


class UnderstandSoulRequest(BaseModel):
    user_id: str
    initial_prompt: str


class UnderstandSoulResponse(BaseModel):
    user_id: str
    soul: str


class Query(BaseModel):
    platform: str
    query: str


class GenerateQueriesRequest(BaseModel):
    user_id: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    recent_chats: list[Any] | None = None


class GenerateQueriesResponse(BaseModel):
    queries: list[Query]


class RankRequest(BaseModel):
    user_id: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    raw_results: list[dict[str, Any] | Any]


class RankedItem(BaseModel):
    id: str
    type: str
    platform: str
    url: str
    title: str
    manifestation_note: str
    score: float


class RankResponse(BaseModel):
    items: list[RankedItem]


class ChatRequest(BaseModel):
    user_id: str
    message: str
    user_goal: str
    user_profile: dict[str, Any] | None = None
    chat_history: list[Any] | None = None
    current_content_ids: list[str] | None = None


class ChatResponse(BaseModel):
    chat_response: str
    needs_new_content: bool
    search_queries: list[Query] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/understand-soul", response_model=UnderstandSoulResponse)
def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    soul = req.initial_prompt.strip()
    return UnderstandSoulResponse(user_id=req.user_id, soul=soul)


@app.post("/agent/generate-queries", response_model=GenerateQueriesResponse)
def generate_queries(req: GenerateQueriesRequest) -> GenerateQueriesResponse:
    goal = req.user_goal.strip() if req.user_goal else "career growth"
    queries = [
        Query(platform="youtube", query=goal),
        Query(platform="pinterest", query=goal),
        Query(platform="reddit", query=goal),
    ]
    return GenerateQueriesResponse(queries=queries)


@app.post("/agent/rank", response_model=RankResponse)
def rank(req: RankRequest) -> RankResponse:
    items: list[RankedItem] = []
    for idx, raw in enumerate(req.raw_results):
        item = raw if isinstance(raw, dict) else {}
        items.append(
            RankedItem(
                id=str(item.get("id", f"item-{idx+1}")),
                type=str(item.get("type", "unknown")),
                platform=str(item.get("platform", "unknown")),
                url=str(item.get("url", "")),
                title=str(item.get("title", "")),
                manifestation_note="Aligned with your goal.",
                score=float(item.get("score", 0.5)),
            )
        )
    items.sort(key=lambda x: x.score, reverse=True)
    return RankResponse(items=items)


@app.post("/agent/chat", response_model=ChatResponse)
def chat(_req: ChatRequest) -> ChatResponse:
    return ChatResponse(
        chat_response="Got it. I can fetch content aligned with your goal.",
        needs_new_content=True,
        search_queries=None,
    )
