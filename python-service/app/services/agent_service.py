from app.llm.client import LLMClient
from app.llm.prompts import build_goal_prompt
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    GenerateContentRequest,
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


# Handles /agent/generate-content: full flow (queries from initial_prompt + enhanced_profile + preferences + recent_chats).
async def generate_content(req: GenerateContentRequest) -> list[ContentItem]:
    limit = max(0, min(req.limit, 100))
    return await orchestrator_fetch_content(
        user_id=req.user_id,
        initial_prompt=req.initial_prompt or "",
        enhanced_profile=req.enhanced_profile or "",
        preferences=req.preferences,
        recent_chats=req.recent_chats,
        limit=limit,
    )


# Handles /agent/chat: LLM reply and whether new content is needed.
def chat(req: ChatRequest) -> ChatResponse:
    prompt = build_goal_prompt(req.user_goal, req.user_profile)
    _ = _llm_client.generate_text(prompt)
    return ChatResponse(
        chat_response="Got it. I can fetch content aligned with your goal.",
        needs_new_content=True,
        search_queries=None,
    )
