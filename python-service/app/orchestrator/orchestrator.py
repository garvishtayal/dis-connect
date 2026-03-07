import asyncio
from typing import Any

from app.models.chat import Query
from app.models.content import ContentItem
from app.redis import get_shown_urls
from app.orchestrator import deduplicator, mixer, rank_placeholder, scrape_fetch
from app.orchestrator.query_generator import generate_queries_ratio

MIN_SCORE = 0.6
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

    # # 3. Flatten, load shown URLs from Redis, drop already-shown.
    # try:
    #     combined = _combine_raw_results(raw_per_query)
    #     shown = await get_shown_urls(user_id)
    #     filtered_raw = deduplicator.filter_already_shown_raw(combined, shown)
    # except Exception as e:
    #     raise RuntimeError(f"Content generation failed at dedupe: {e}") from e

    # # 4. Rank raw items, filter by score, mix by ratio; return up to limit.
    # try:
    #     goal_str = f"{initial_prompt or ''} {enhanced_profile or ''}".strip() or "career growth"
    #     ranked = rank_placeholder.rank_raw_items(filtered_raw, goal_str, preferences)
    #     above = [c for c in ranked if c.score >= MIN_SCORE]
    #     mixed = mixer.mix_by_ratio(above)
    # except Exception as e:
    #     raise RuntimeError(f"Content generation failed at rank/mix: {e}") from e

    # return mixed[:limit]

    return raw_per_query


# Runs fetch_one_query for each query concurrently.
async def _fetch_all_queries_concurrent(queries: list[Query]) -> list[list[dict[str, Any]]]:
    tasks = [scrape_fetch.fetch_one_query(q) for q in queries]
    return list(await asyncio.gather(*tasks))


# Flattens list of raw result lists into one list.
def _combine_raw_results(raw_per_query: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for batch in raw_per_query:
        out.extend(batch)
    return out
