"""Rank raw scraped items with LLM; score 0-1 per item."""
import json
import re
from typing import Any

from app.llm.client import generate_text
from app.llm.prompts import SYSTEM_PROMPTS, build_rank_prompt
from app.models.content import ContentItem

MAX_ITEMS_FOR_RANK = 80
DEFAULT_SCORE = 0.5


# One line per item: id, type, platform, title (for LLM context).
def _items_summary(raw: list[dict[str, Any]]) -> str:
    lines = []
    for r in raw[:MAX_ITEMS_FOR_RANK]:
        tid = r.get("id", "")
        t = r.get("type", "")
        plat = r.get("platform", "")
        title = (r.get("title") or "")[:80]
        lines.append(f"id: {tid}, type: {t}, platform: {plat}, title: {title}")
    return "\n".join(lines)


# Parse LLM JSON array into id -> score.
def _parse_rank_response(raw: str) -> dict[str, float]:
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, list):
        return {}
    out: dict[str, float] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        id_ = item.get("id") or ""
        if not id_:
            continue
        try:
            score = float(item.get("score", DEFAULT_SCORE))
            score = max(0.0, min(1.0, score))
        except (TypeError, ValueError):
            score = DEFAULT_SCORE
        out[id_] = score
    return out


# Rank raw items via LLM (build_rank_prompt); return ContentItems with score.
def rank_raw_items(
    raw: list[dict[str, Any]],
    initial_prompt: str,
    enhanced_profile: str,
    recent_chats: list[Any] | None,
) -> list[ContentItem]:
    if not raw:
        return []
    items_summary = _items_summary(raw)
    user_prompt = build_rank_prompt(initial_prompt, enhanced_profile, recent_chats, items_summary)
    full_prompt = f"{SYSTEM_PROMPTS['ranking']}\n\n{user_prompt}"
    response = generate_text(full_prompt)
    scores_by_id = _parse_rank_response(response) if response else {}
    result: list[ContentItem] = []
    for r in raw:
        id_ = r.get("id", "")
        score = scores_by_id.get(id_, DEFAULT_SCORE)
        result.append(
            ContentItem(
                id=id_,
                type=str(r.get("type", "unknown")),
                platform=str(r.get("platform", "unknown")),
                url=str(r.get("url", "")),
                title=str(r.get("title", "")),
                score=score,
                metadata=r.get("metadata"),
            )
        )
    return result
