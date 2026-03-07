from app.llm.client import LLMClient
from app.llm.prompts import build_goal_prompt
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    GenerateContentRequest,
    Query,
    UnderstandSoulRequest,
    UnderstandSoulResponse,
)
from app.models.content import ContentItem
from app.orchestrator.orchestrator import fetch_content as orchestrator_fetch_content

_llm_client = LLMClient()


# Handles /agent/understand-soul: derive soul from initial prompt.
def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    soul = req.initial_prompt.strip()
    return UnderstandSoulResponse(user_id=req.user_id, soul=soul)


# Handles /agent/generate-content: queries + scrape + mix + rank, return items (placeholder).
async def generate_content(req: GenerateContentRequest) -> list[ContentItem]:
    goal = req.user_goal.strip() if req.user_goal else "career growth"
    queries = [
        Query(platform="youtube", query=goal),
        Query(platform="pinterest", query=goal),
        Query(platform="reddit", query=goal),
    ]
    items = await orchestrator_fetch_content(queries)
    limit = max(0, min(req.limit, 100))
    return items[:limit]


# Handles /agent/chat: LLM reply and whether new content is needed.
def chat(req: ChatRequest) -> ChatResponse:
    prompt = build_goal_prompt(req.user_goal, req.user_profile)
    _ = _llm_client.generate_text(prompt)
    return ChatResponse(
        chat_response="Got it. I can fetch content aligned with your goal.",
        needs_new_content=True,
        search_queries=None,
    )
