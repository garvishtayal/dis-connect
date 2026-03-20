import asyncio
import re
from typing import Any

from app.models.chat import Query
from app.models.content import ContentItem
from app.redis import get_cached_queries, get_shown_urls, set_cached_queries
from app.orchestrator import deduplicator, mixer, ranker, scrape_fetch
from app.orchestrator.query_generator import generate_queries_ratio

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
    # 1. Generate queries via LLM; on failure fall back to last cached queries, then to keyword fallback.
    queries: list[Query] = []
    try:
        queries = generate_queries_ratio(initial_prompt, enhanced_profile, preferences, recent_chats)
        # Persist successful queries so future requests can reuse them if LLM is down.
        await set_cached_queries(user_id, [{"platform": q.platform, "query": q.query} for q in queries])
        by_platform = {}
        for q in queries:
            by_platform[q.platform] = by_platform.get(q.platform, 0) + 1
        print(f"[orchestrator] queries generated (LLM): {by_platform}")
    except Exception as e:
        print(f"[orchestrator] query LLM failed ({e}), trying cached queries")
        cached = await get_cached_queries(user_id)
        if cached:
            queries = [Query(platform=c["platform"], query=c["query"]) for c in cached]
            print(f"[orchestrator] using {len(queries)} cached queries")
        else:
            queries = _fallback_queries(initial_prompt, enhanced_profile)
            print(f"[orchestrator] using {len(queries)} keyword-fallback queries")

    # 2. Fetch raw results per query; individual failures return [] (logged in scrape_fetch).
    raw_per_query = await _fetch_all_queries_concurrent(queries)

    # 3. Flatten, dedupe by id, load shown URLs from Redis, drop already-shown.
    try:
        combined = _combine_raw_results(raw_per_query)
        by_type_raw = {}
        for r in combined:
            t = r.get("type", "unknown")
            by_type_raw[t] = by_type_raw.get(t, 0) + 1
        print(f"[orchestrator] raw combined: {len(combined)} items → by type: {by_type_raw}")
        combined = _dedupe_raw_by_id(combined)
        shown = await get_shown_urls(user_id)
        filtered_raw = deduplicator.filter_already_shown_raw(combined, shown)
        print(f"[orchestrator] after dedupe+shown filter: {len(filtered_raw)} items")
    except Exception as e:
        raise RuntimeError(f"Content generation failed at dedupe: {e}") from e

    # 4. Rank raw items via LLM, mix top-N by score; mixer already sorts descending so no MIN_SCORE filter needed.
    try:
        ranked = ranker.rank_raw_items(filtered_raw, initial_prompt or "", enhanced_profile or "", recent_chats)
        mixed = mixer.mix_by_ratio(ranked, limit=limit)
        final = mixed[:limit]
        by_type_final = {}
        for c in final:
            by_type_final[c.type] = by_type_final.get(c.type, 0) + 1
        print(f"[orchestrator] final mix: {len(final)} items → by type: {by_type_final}")
        if not final:
            raise RuntimeError("Content generation produced no items")
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


# Builds simple 4 Pinterest + 3 YouTube queries from raw profile text without calling an LLM.
# Used only when both LLM and Redis query cache are unavailable.
def _fallback_queries(initial_prompt: str, enhanced_profile: str) -> list[Query]:
    text = f"{initial_prompt} {enhanced_profile}".strip()
    # Extract meaningful words (4+ chars, alpha only), deduplicate while preserving order.
    words = re.findall(r"[a-zA-Z]{4,}", text)
    seen: set[str] = set()
    keywords: list[str] = []
    for w in words:
        lw = w.lower()
        if lw not in seen:
            seen.add(lw)
            keywords.append(lw)

    # Build phrases by pairing consecutive keywords; fall back to "lifestyle inspiration" if empty.
    phrases = [f"{keywords[i]} {keywords[i + 1]}" for i in range(0, min(len(keywords) - 1, 8), 2)]
    if not phrases:
        phrases = ["lifestyle inspiration", "personal growth", "motivation"]

    pin_queries = (phrases + ["lifestyle inspiration", "aesthetic goals", "motivation workspace"])[:4]
    yt_queries = (phrases + ["day in life motivation", "self improvement routine", "lifestyle goals"])[:3]

    return (
        [Query(platform="pinterest", query=q) for q in pin_queries]
        + [Query(platform="youtube", query=q) for q in yt_queries]
    )
