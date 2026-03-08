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


# Builds pipeline raw dict from one pin URL and keyword via PinRawItem (url may be str or HttpUrl).
def _url_to_raw(url: Any, keyword: str, index: int) -> dict[str, Any]:
    url_str = str(url)
    pin_id = _url_to_pin_id(url_str, index)
    item = PinRawItem(id=f"pin-{pin_id}", url=url_str, title=keyword or "Pinterest pin")
    return item.to_dict()


# Runs Pinterest keyword search via pinscrape (sync), returns list of raw dicts.
def _search_pinterest_sync(query: str, max_results: int = 25) -> list[dict[str, Any]]:
    print("[pin] 1 search", query)
    Pinterest.BASE_URL = "https://www.pinterest.com"
    scraper = Pinterest(proxies={}, sleep_time=1)
    try:
        url_list = scraper.search(query, max_results)
        print("[pin] 2 urls", len(url_list) if isinstance(url_list, list) else 0)
    except Exception as e:
        print("[pin] err:", e)
        return []
    if not isinstance(url_list, list) or not url_list:
        return []
    out = [_url_to_raw(u, query, i) for i, u in enumerate(url_list)]
    print("[pin] 3 ok", len(out))
    return out


# Search Pinterest by query, return raw dicts for image pins (async, runs in thread).
async def search(query: str) -> list[dict[str, Any]]:
    try:
        return await asyncio.to_thread(_search_pinterest_sync, query, 25)
    except Exception as e:
        print("[pin] err async:", e)
        return []
