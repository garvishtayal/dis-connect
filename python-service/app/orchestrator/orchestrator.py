import asyncio
from typing import Any

from app.models.chat import Query
from app.models.content import ContentItem
from app.redis import get_shown_urls
from app.orchestrator import deduplicator, mixer, rank_placeholder, scrape_fetch
from app.orchestrator.query_generator import generate_queries_ratio

MIN_SCORE = 0.6
TARGET_ITEMS = 40


# Main entry: returns ranked content after cache-or-scrape, dedupe, rank, filter, mix.
async def fetch_content(
    user_id: str,
    initial_prompt: str,
    enhanced_profile: str,
    preferences: dict[str, Any] | None,
    recent_chats: list[Any] | None,
    limit: int = TARGET_ITEMS,
) -> list[ContentItem]:
    # 1. Generate queries in ratio (photos / shorts / videos); placeholder or LLM later.
    queries = generate_queries_ratio(initial_prompt, enhanced_profile, preferences, recent_chats)
    # 2. For each query: cache hit or scrape then cache; run all concurrently.
    raw_per_query = await _fetch_all_queries_concurrent(queries)
    # 3. Flatten per-query results into one list of raw items.
    combined = _combine_raw_results(raw_per_query)
    # 4. Load already-shown URLs from Redis (user:{id}:shown).
    shown = await get_shown_urls(user_id)
    # 5. Drop raw items whose URL is in shown (dedup before rank).
    filtered_raw = deduplicator.filter_already_shown_raw(combined, shown)
    # 6. Rank each item (placeholder score; LLM later) and build ContentItems.
    goal_str = f"{initial_prompt or ''} {enhanced_profile or ''}".strip() or "career growth"
    ranked = rank_placeholder.rank_raw_items(filtered_raw, goal_str, preferences)
    # 7. Keep only items with score >= MIN_SCORE.
    above = [c for c in ranked if c.score >= MIN_SCORE]
    # 8. Mix by ratio: 16 image, 16 short, 8 video (by platform).
    mixed = mixer.mix_by_ratio(above)
    # 9. Return up to limit items.
    return mixed[:limit]


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
