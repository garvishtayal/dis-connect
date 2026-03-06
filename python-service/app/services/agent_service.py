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

_llm_client = LLMClient()


# Handles understanding a user's initial soul prompt.
def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    soul = req.initial_prompt.strip()
    return UnderstandSoulResponse(user_id=req.user_id, soul=soul)


# Handles generation of platform search queries from the user's goal.
def generate_queries(req: GenerateQueriesRequest) -> GenerateQueriesResponse:
    goal = req.user_goal.strip() if req.user_goal else "career growth"
    queries = [
        Query(platform="youtube", query=goal),
        Query(platform="pinterest", query=goal),
        Query(platform="reddit", query=goal),
    ]
    return GenerateQueriesResponse(queries=queries)


# Handles ranking of raw content items into structured ranked items.
def rank(req: RankRequest) -> RankResponse:
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


# Handles chat requests and indicates whether new content should be fetched.
def chat(req: ChatRequest) -> ChatResponse:
    prompt = build_goal_prompt(req.user_goal, req.user_profile)
    _ = _llm_client.generate_text(prompt)
    return ChatResponse(
        chat_response="Got it. I can fetch content aligned with your goal.",
        needs_new_content=True,
        search_queries=None,
        manifestation_tip=None,
    )

