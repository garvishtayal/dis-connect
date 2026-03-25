"""Pinterest scraper: keyword search via pinscrape; accepts optional proxy URL from Go worker."""
import asyncio
import hashlib
import re
from typing import Any

from pinscrape import Pinterest

from app.scrapers.models import PinRawItem

PIN_ID_PATTERN = re.compile(r"/pin/([^/]+)/?")


def _url_to_pin_id(url: str) -> str:
    m = PIN_ID_PATTERN.search(url)
    return m.group(1) if m else hashlib.sha256(url.encode()).hexdigest()[:16]


def _url_to_raw(url: Any, keyword: str) -> dict[str, Any]:
    url_str = str(url)
    pin_id = _url_to_pin_id(url_str)
    item = PinRawItem(id=f"pin-{pin_id}", url=url_str, title=keyword or "Pinterest pin")
    return item.to_dict()


def _build_proxies(proxy_url: str) -> dict[str, str]:
    """Convert a proxy URL string to requests-style proxy dict."""
    if not proxy_url:
        return {}
    return {"http": proxy_url, "https": proxy_url}


def _search_sync(query: str, proxy_url: str, max_results: int = 25) -> list[dict[str, Any]]:
    Pinterest.BASE_URL = "https://www.pinterest.com"
    proxies = _build_proxies(proxy_url)
    scraper = Pinterest(proxies=proxies, sleep_time=1)
    try:
        url_list = scraper.search(query, max_results)
    except Exception:
        raise RuntimeError("Pinterest scrape failed")
    if not isinstance(url_list, list) or not url_list:
        return []
    return [_url_to_raw(u, query) for u in url_list]


async def search(query: str, proxy: str = "") -> list[dict[str, Any]]:
    """Search Pinterest by query (25 pins max); proxy is an optional URL assigned by Go worker."""
    try:
        out = await asyncio.to_thread(_search_sync, query, proxy, 25)
        print(f"[pinterest] scrape done ({len(out)} items)")
        return out
    except Exception:
        raise RuntimeError("Pinterest scrape failed")
