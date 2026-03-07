from typing import Any

from app.models.chat import Query
from app.redis import get_search_cached, set_search_cached
from app.scrapers import instagram, pinterest, youtube


# Fetches raw results for one query: cache hit or scrape then cache; content_type in key for YT/IG.
async def fetch_one_query(q: Query) -> list[dict[str, Any]]:
    content_type = q.content_type if q.platform in ("youtube", "instagram") else ""
    cached = await get_search_cached(q.platform, q.query, content_type)
    if cached is not None:
        return cached
    if q.platform == "pinterest":
        results = await pinterest.search(q.query)
    elif q.platform == "instagram":
        results = await instagram.search(q.query, q.content_type)
    elif q.platform == "youtube":
        results = await youtube.search(q.query, q.content_type)
    else:
        results = []
    await set_search_cached(q.platform, q.query, results, content_type)
    return results
