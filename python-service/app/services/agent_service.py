import json
import re

from app.llm.client import LLMClient
from app.llm.prompts import (
    SYSTEM_PROMPTS,
    build_chat_prompt,
    build_enhance_profile_prompt,
    build_preferences_prompt,
    parse_chat_response,
)
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    GenerateContentRequest,
    PreferencesRequest,
    PreferencesResponse,
    Query,
    UnderstandSoulRequest,
    UnderstandSoulResponse,
)
from app.llm.query_generator import generate_queries_ratio

_llm_client = LLMClient()


# Handles /agent/understand-soul: LLM derives soul from initial_prompt + recent_chats.
def understand_soul(req: UnderstandSoulRequest) -> UnderstandSoulResponse:
    prompt = build_enhance_profile_prompt(req.initial_prompt, req.recent_chats)
    soul = _llm_client.generate_text(prompt) or req.initial_prompt.strip()
    return UnderstandSoulResponse(user_id=req.user_id, soul=soul)


# Handles /agent/generate-queries: LLM generates platform search queries for Go workers to execute.
def generate_queries(req: GenerateContentRequest) -> list[Query]:
    return generate_queries_ratio(
        req.initial_prompt or "",
        req.enhanced_profile or "",
        req.preferences,
        req.recent_chats,
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


# Handles /preferences: LLM updates user content preferences JSON.
def preferences(req: PreferencesRequest) -> PreferencesResponse:
    user_prompt = build_preferences_prompt(
        chat_history=req.recent_chats,
        preferences=req.preferences,
    )
    full_prompt = f"{SYSTEM_PROMPTS['preferences']}\n\n{user_prompt}"
    raw = _llm_client.generate_text(full_prompt)

    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError("preferences response is not an object")
    except Exception:
        # Fallback: keep existing or sensible default shape.
        data = req.preferences or {
            "content_filter": ["image", "short", "video"],
            "avoid_topics": [],
            "notes": "",
        }

    return PreferencesResponse(preferences=data)
