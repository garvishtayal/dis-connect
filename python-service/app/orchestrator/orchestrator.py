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
    user_goal: str,
    user_profile: dict[str, Any] | None,
    limit: int = TARGET_ITEMS,
) -> list[ContentItem]:
    queries = generate_queries_ratio(user_goal)
    raw_per_query = await _fetch_all_queries_concurrent(queries)
    combined = _combine_raw_results(raw_per_query)
    shown = await get_shown_urls(user_id)
    filtered_raw = deduplicator.filter_already_shown_raw(combined, shown)
    ranked = rank_placeholder.rank_raw_items(filtered_raw, user_goal, user_profile)
    above = [c for c in ranked if c.score >= MIN_SCORE]
    mixed = mixer.mix_by_ratio(above)
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
