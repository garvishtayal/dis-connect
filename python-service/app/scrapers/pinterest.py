"""Pinterest scraper: keyword search via pinscrape; return photo pins as raw dicts for pipeline."""
import asyncio
import re
from typing import Any

from pinscrape import Pinterest

from app.scrapers.models import PinRawItem

PIN_ID_PATTERN = re.compile(r"/pin/([^/]+)/?")


# Extracts pin id from Pinterest URL or returns index-based fallback.
def _url_to_pin_id(url: str, index: int) -> str:
    m = PIN_ID_PATTERN.search(url)
    return m.group(1) if m else f"pin-{index}"


# Builds pipeline raw dict from one pin URL and keyword via PinRawItem.
def _url_to_raw(url: str, keyword: str, index: int) -> dict[str, Any]:
    pin_id = _url_to_pin_id(url, index)
    item = PinRawItem(id=f"pin-{pin_id}", url=url, title=keyword or "Pinterest pin")
    return item.to_dict()


# Runs Pinterest keyword search via pinscrape (sync), returns list of raw dicts.
def _search_pinterest_sync(query: str, max_results: int = 25) -> list[dict[str, Any]]:
    p = Pinterest(proxies={}, sleep_time=1)
    try:
        url_list = p.search(query, max_results)
    except Exception:
        return []
    if not isinstance(url_list, list) or not url_list:
        return []
    return [_url_to_raw(u, query, i) for i, u in enumerate(url_list)]


# Search Pinterest by query, return raw dicts for image pins (async, runs in thread).
async def search(query: str) -> list[dict[str, Any]]:
    try:
        return await asyncio.to_thread(_search_pinterest_sync, query, 25)
    except Exception:
        return []
