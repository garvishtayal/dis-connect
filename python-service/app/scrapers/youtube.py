"""YouTube scraper: search via yt-dlp, return shorts and videos as raw dicts for pipeline."""
import asyncio
from typing import Any

import yt_dlp

from app.scrapers.models import YtRawItem

# Shorts: duration <= 60s or "/shorts/" in URL; else video.
SHORTS_MAX_DURATION_SEC = 60


# True if entry is a Short (duration ≤60s or /shorts/ in URL), else False.
def _is_short(entry: dict[str, Any] | None) -> bool:
    if not entry:
        return False
    url = (entry.get("webpage_url") or entry.get("url") or "") or ""
    if "/shorts/" in url:
        return True
    dur = entry.get("duration")
    if dur is not None and isinstance(dur, (int, float)):
        return float(dur) <= SHORTS_MAX_DURATION_SEC
    return False


# Converts one yt-dlp entry to pipeline raw dict via YtRawItem.
def _entry_to_raw(entry: dict[str, Any], content_type: str) -> dict[str, Any]:
    vid_id = entry.get("id") or ""
    url = entry.get("webpage_url") or entry.get("url") or f"https://www.youtube.com/watch?v={vid_id}"
    title = entry.get("title") or "YouTube"
    item = YtRawItem(
        id=f"yt-{content_type}-{vid_id}",
        type=content_type,
        url=url,
        title=title,
        metadata={"duration": entry.get("duration"), "duration_string": entry.get("duration_string")},
    )
    return item.to_dict()


# Runs ytsearch for query (sync), returns list of raw entries; no download.
def _search_youtube_sync(query: str, max_results: int = 20) -> list[dict[str, Any]]:
    opts = {"quiet": True, "no_warnings": True, "extract_flat": False, "skip_download": True, "default_search": "ytsearch"}
    search_url = f"ytsearch{max_results}:{query}"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(search_url, download=False)
    if not info or "entries" not in info:
        return []
    entries = [e for e in info["entries"] if e]
    return entries


# Keeps only entries matching content_type ("short" or "video").
def _filter_by_content_type(entries: list[dict[str, Any]], content_type: str) -> list[dict[str, Any]]:
    shorts = [e for e in entries if _is_short(e)]
    videos = [e for e in entries if not _is_short(e)]
    return shorts if content_type == "short" else videos


# Search YouTube by query, return raw dicts for shorts or videos per content_type (async, runs in thread).
async def search(query: str, content_type: str = "video") -> list[dict[str, Any]]:
    try:
        entries = await asyncio.to_thread(_search_youtube_sync, query, 30)
        filtered = _filter_by_content_type(entries, content_type)
        return [_entry_to_raw(e, content_type) for e in filtered]
    except Exception:
        return []
