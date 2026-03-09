from app.llm.client import LLMClient
from app.llm.prompts import (
    SYSTEM_PROMPTS,
    build_chat_prompt,
    build_enhance_profile_prompt,
    parse_chat_response,
)
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


# Handles /agent/understand-soul: LLM derives soul from initial_prompt + recent_chats.
def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    prompt = build_enhance_profile_prompt(req.initial_prompt, req.recent_chats)
    soul = _llm_client.generate_text(prompt) or req.initial_prompt.strip()
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


# Handles /agent/chat: LLM reply and needs_new_content flag (parsed from structured JSON).
def chat(req: ChatRequest) -> ChatResponse:
    initial_prompt = req.initial_prompt or ""
    enhanced_profile = req.enhanced_profile or ""
    user_prompt = build_chat_prompt(req.message, initial_prompt, enhanced_profile, req.recent_chats)
    full_prompt = f"{SYSTEM_PROMPTS['chat']}\n\n{user_prompt}"
    raw = _llm_client.generate_text(full_prompt)
    chat_response, needs_new_content = parse_chat_response(raw)
    return ChatResponse(
        chat_response=chat_response,
        needs_new_content=needs_new_content,
    )
