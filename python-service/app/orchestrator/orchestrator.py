import asyncio
from typing import Any

from app.models.chat import Query
from app.models.content import ContentItem
from app.redis import get_shown_urls
from app.orchestrator import deduplicator, mixer, ranker, scrape_fetch
from app.orchestrator.query_generator import generate_queries_ratio

MIN_SCORE = 0.5  # include unscored (default 0.5) so Pinterest etc. not dropped when LLM omits or truncates
TARGET_ITEMS = 40


# Main entry: returns ranked content after cache-or-scrape, dedupe, rank, filter, mix; raises with clear step on failure.
async def fetch_content(
    user_id: str,
    initial_prompt: str,
    enhanced_profile: str,
    preferences: dict[str, Any] | None,
    recent_chats: list[Any] | None,
    limit: int = TARGET_ITEMS,
) -> list[ContentItem]:
    # 1. Generate queries in ratio (LLM); raise on empty/invalid JSON.
    try:
        queries = generate_queries_ratio(initial_prompt, enhanced_profile, preferences, recent_chats)
    except Exception as e:
        raise RuntimeError(f"Content generation failed at query generation: {e}") from e

    # 2. Fetch raw results per query (cache or scrape), concurrent.
    try:
        raw_per_query = await _fetch_all_queries_concurrent(queries)
    except Exception as e:
        raise RuntimeError(f"Content generation failed at fetch/scrape: {e}") from e

    # 3. Flatten, dedupe by id, load shown URLs from Redis, drop already-shown.
    try:
        combined = _combine_raw_results(raw_per_query)
        combined = _dedupe_raw_by_id(combined)
        shown = await get_shown_urls(user_id)
        filtered_raw = deduplicator.filter_already_shown_raw(combined, shown)
    except Exception as e:
        raise RuntimeError(f"Content generation failed at dedupe: {e}") from e

    # 4. Rank raw items via LLM, filter by score, mix by ratio; return up to limit.
    try:
        ranked = ranker.rank_raw_items(filtered_raw, initial_prompt or "", enhanced_profile or "", recent_chats)
        above = [c for c in ranked if c.score >= MIN_SCORE]
        mixed = mixer.mix_by_ratio(above, limit=limit)
        final = mixed[:limit]
    except Exception as e:
        raise RuntimeError(f"Content generation failed at rank/mix: {e}") from e

    return final


# Runs fetch_one_query for each query sequentially (avoids Pinterest rate/connection issues).
async def _fetch_all_queries_concurrent(queries: list[Query]) -> list[list[dict[str, Any]]]:
    out: list[list[dict[str, Any]]] = []
    for q in queries:
        out.append(await scrape_fetch.fetch_one_query(q))
    return out


# Deduplicates raw items by id (keeps first occurrence).
def _dedupe_raw_by_id(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for r in raw:
        id_ = r.get("id", "")
        if id_ in seen:
            continue
        seen.add(id_)
        out.append(r)
    return out


# Flattens list of raw result lists into one list.
def _combine_raw_results(raw_per_query: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for batch in raw_per_query:
        out.extend(batch)
    return out
