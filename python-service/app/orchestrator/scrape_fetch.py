from typing import Any

from app.models.chat import Query
from app.redis import get_search_cached, set_search_cached
from app.scrapers import pinterest, youtube


# Fetches raw results for one query: cache hit or scrape then cache.
async def fetch_one_query(q: Query) -> list[dict[str, Any]]:
    cached = await get_search_cached(q.platform, q.query, "")
    if cached is not None:
        return cached
    if q.platform == "pinterest":
        results = await pinterest.search(q.query)
    elif q.platform == "youtube":
        results = []  # skip for now to avoid API limit
    else:
        results = []
    await set_search_cached(q.platform, q.query, results, "")
    return results
