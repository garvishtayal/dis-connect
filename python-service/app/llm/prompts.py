from typing import Any

# -----------------------------------------------------------------------------
# All LLM prompts live here. One builder per use case; call from:
#   - Chat:          agent_service.chat          -> build_chat_prompt
#   - Generate query: query_generator (orchestrator) -> build_query_generation_prompt
#   - Enhance profile: understand_soul / profile step -> build_enhance_profile_prompt
#   - Preferences:    preferences update (Go or Python) -> build_preferences_prompt
#   - Rank:          rank_placeholder           -> build_rank_prompt
# -----------------------------------------------------------------------------


# Chat: reply + needs_new_content. Input: message, goal, profile, history.
def build_chat_prompt(
    message: str,
    user_goal: str,
    user_profile: dict[str, Any] | None = None,
    chat_history: list[Any] | None = None,
) -> str:
    profile_snippet = f" Profile: {user_profile!r}" if user_profile else ""
    history_snippet = f" Recent: {chat_history!r}" if chat_history else ""
    return f"User message: {message}. Goal: {user_goal}.{profile_snippet}{history_snippet}"


# Generate queries: returns JSON list of {platform, query, content_type}. Input: prompt + profile + preferences + recent_chats + ratio instructions.
def build_query_generation_prompt(
    initial_prompt: str,
    enhanced_profile: str,
    preferences: dict[str, Any] | None,
    recent_chats: list[Any] | None,
) -> str:
    prefs = f" Preferences: {preferences}" if preferences else ""
    chats = f" Recent chats: {recent_chats}" if recent_chats else ""
    return (
        f"Initial prompt: {initial_prompt}. Enhanced profile: {enhanced_profile}.{prefs}{chats}\n"
        "Generate search queries in ratio: 40% photos (Pinterest, Instagram), 40% shorts/reels (Instagram Reels, YouTube Shorts), 20% videos (YouTube). "
        "Return a JSON array of objects with keys: platform, query, content_type. Example: [{\"platform\":\"pinterest\",\"query\":\"...\",\"content_type\":\"image\"}]."
    )


# Enhance profile: turns initial_prompt (+ optional history) into enhanced_profile text.
def build_enhance_profile_prompt(initial_prompt: str, chat_history: list[Any] | None = None) -> str:
    history_snippet = f" Chat history: {chat_history}" if chat_history else ""
    return f"Given this user initial prompt, produce a short enhanced profile (soul) description.{history_snippet}\nInitial prompt: {initial_prompt}"


# Preferences: generate or update preferences from recent behavior/chats.
def build_preferences_prompt(
    recent_chats: list[Any] | None = None,
    current_preferences: dict[str, Any] | None = None,
) -> str:
    chats = f" Recent chats: {recent_chats}" if recent_chats else ""
    prefs = f" Current preferences: {current_preferences}" if current_preferences else ""
    return f"Update or generate user content preferences (e.g. content_filter).{chats}{prefs}\nReturn JSON object with preference keys."


# Rank: score each raw item 0-1 (and optional manifestation_note). Input: summary of items + goal + preferences.
def build_rank_prompt(
    items_summary: str,
    goal_str: str,
    preferences: dict[str, Any] | None = None,
) -> str:
    prefs = f" Preferences: {preferences}" if preferences else ""
    return (
        f"User goal: {goal_str}.{prefs}\n"
        f"Score each of these content items 0-1 for relevance to the goal. Items:\n{items_summary}\n"
        "Return JSON array of objects with keys: id (or index), score, manifestation_note (short string)."
    )


# Legacy: simple goal prompt (used by chat placeholder).
def build_goal_prompt(user_goal: str, user_profile: dict[str, Any] | None = None) -> str:
    profile_snippet = f" Profile: {user_profile!r}" if user_profile else ""
    return f"User goal: {user_goal}.{profile_snippet}"

