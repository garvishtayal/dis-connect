from typing import Any

# -----------------------------------------------------------------------------
# All LLM prompts live here. One builder per use case; call from:
#   - Chat:          agent_service.chat          -> build_chat_prompt
#   - Generate query: query_generator (orchestrator) -> build_query_generation_prompt
#   - Enhance profile: understand_soul / profile step -> build_enhance_profile_prompt
#   - Preferences:    preferences update (Go or Python) -> build_preferences_prompt
#   - Rank:          rank_placeholder           -> build_rank_prompt
# -----------------------------------------------------------------------------


# Chat: message, initial_prompt, enhanced_profile, chat_history.
def build_chat_prompt(
    message: str,
    initial_prompt: str,
    enhanced_profile: str,
    chat_history: list[Any] | None = None,
) -> str:
    history_snippet = f" Chat history: {chat_history}" if chat_history else ""
    return f"Message: {message}. Initial prompt: {initial_prompt}. Enhanced profile: {enhanced_profile}.{history_snippet}"


# Generate queries: initial_prompt, enhanced_profile, preferences, chat_history.
def build_query_generation_prompt(
    initial_prompt: str,
    enhanced_profile: str,
    preferences: dict[str, Any] | None,
    chat_history: list[Any] | None,
) -> str:
    prefs = f" Preferences: {preferences}" if preferences else ""
    history_snippet = f" Chat history: {chat_history}" if chat_history else ""
    return (
        f"Initial prompt: {initial_prompt}. Enhanced profile: {enhanced_profile}.{prefs}{history_snippet}\n"
        "Generate search queries in ratio: 40% photos (Pinterest, Instagram), 40% shorts/reels (Instagram Reels, YouTube Shorts), 20% videos (YouTube). "
        "Return a JSON array of objects with keys: platform, query, content_type. Example: [{\"platform\":\"pinterest\",\"query\":\"...\",\"content_type\":\"image\"}]."
    )


# Enhance profile: initial_prompt, chat_history.
def build_enhance_profile_prompt(initial_prompt: str, chat_history: list[Any] | None = None) -> str:
    history_snippet = f" Chat history: {chat_history}" if chat_history else ""
    return f"Given this user initial prompt, produce a short enhanced profile (soul) description.{history_snippet}\nInitial prompt: {initial_prompt}"


# Preferences: chat_history, preferences.
def build_preferences_prompt(
    chat_history: list[Any] | None = None,
    preferences: dict[str, Any] | None = None,
) -> str:
    history_snippet = f" Chat history: {chat_history}" if chat_history else ""
    prefs = f" Preferences: {preferences}" if preferences else ""
    return f"Update or generate user content preferences (e.g. content_filter).{history_snippet}{prefs}\nReturn JSON object with preference keys."


# Rank: initial_prompt, enhanced_profile, chat_history, items_summary.
def build_rank_prompt(
    initial_prompt: str,
    enhanced_profile: str,
    chat_history: list[Any] | None,
    items_summary: str,
) -> str:
    history_snippet = f" Chat history: {chat_history}" if chat_history else ""
    return (
        f"Initial prompt: {initial_prompt}. Enhanced profile: {enhanced_profile}.{history_snippet}\n"
        f"Score each of these content items 0-1 for relevance. Items:\n{items_summary}\n"
        "Return JSON array of objects with keys: id (or index), score, manifestation_note (short string)."
    )

