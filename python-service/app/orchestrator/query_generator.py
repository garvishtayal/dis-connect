import json
import re
from typing import Any

from app.llm.client import generate_text
from app.llm.prompts import SYSTEM_PROMPTS, build_query_generation_prompt
from app.models.chat import Query


# Uses LLM to generate search queries from user context; raises ValueError on LLM/parse failure.
def generate_queries_ratio(
    initial_prompt: str,
    enhanced_profile: str,
    preferences: dict[str, Any] | None,
    recent_chats: list[Any] | None,
) -> list[Query]:
    user_prompt = build_query_generation_prompt(initial_prompt, enhanced_profile, preferences, recent_chats)
    full_prompt = f"{SYSTEM_PROMPTS['query_generation']}\n\n{user_prompt}"
    raw = generate_text(full_prompt)
    if not raw:
        raise ValueError("Query generation: LLM returned empty response")
    return _parse_query_json(raw)


# Parses LLM JSON array into list[Query]; raises ValueError on invalid JSON or empty/ invalid shape.
def _parse_query_json(raw: str) -> list[Query]:
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Query generation: invalid JSON from LLM: {e}") from e
    if not isinstance(data, list):
        raise ValueError("Query generation: LLM response is not a JSON array")
    out: list[Query] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        platform = item.get("platform") or "pinterest"
        query = item.get("query") or ""
        content_type = item.get("content_type") or "image"
        if query:
            out.append(Query(platform=platform, query=query, content_type=content_type))
    if not out:
        raise ValueError("Query generation: no valid queries in LLM response")
    return out
