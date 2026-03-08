"""YouTube scraper: one query → 10 shorts + 5 videos via YouTube Data API v3; 3 API keys fallback."""
import asyncio
import os
from typing import Any

import requests

from app.scrapers.models import YtRawItem

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
SHORTS_PER_QUERY = 10
VIDEOS_PER_QUERY = 5


def _get_api_keys() -> list[str]:
    # Load up to 3 YouTube API keys from env.
    keys = [os.getenv("YOUTUBE_API_KEY_1"), os.getenv("YOUTUBE_API_KEY_2"), os.getenv("YOUTUBE_API_KEY_3")]
    return [k for k in keys if k]


def _api_search_one(query: str, content_type: str, max_results: int, api_key: str) -> list[dict[str, Any]]:
    # One API call: shorts (videoDuration=short) or videos (medium).
    params = {"part": "id,snippet", "q": query, "type": "video", "maxResults": max_results, "key": api_key}
    params["videoDuration"] = "short" if content_type == "short" else "medium"
    r = requests.get(SEARCH_URL, params=params, timeout=15)
    r.raise_for_status()
    items = (r.json().get("items") or [])
    out = []
    for it in items:
        vid_id = it.get("id", {}).get("videoId")
        if not vid_id:
            continue
        title = (it.get("snippet") or {}).get("title", "YouTube")
        url = f"https://www.youtube.com/shorts/{vid_id}" if content_type == "short" else f"https://www.youtube.com/watch?v={vid_id}"
        raw = YtRawItem(id=f"yt-{content_type}-{vid_id}", type=content_type, url=url, title=title, metadata={})
        out.append(raw.to_dict())
    return out


def _search_sync(query: str, api_key: str) -> list[dict[str, Any]]:
    # Run shorts (10) + videos (5) for one query; combine.
    shorts = _api_search_one(query, "short", SHORTS_PER_QUERY, api_key)
    videos = _api_search_one(query, "video", VIDEOS_PER_QUERY, api_key)
    return shorts + videos


async def search(query: str) -> list[dict[str, Any]]:
    # One query → 10 shorts + 5 videos; try keys in order until one works.
    keys = _get_api_keys()
    for key in keys:
        try:
            out = await asyncio.to_thread(_search_sync, query, key)
            print("youtube scrape done")
            return out
        except Exception:
            continue
    raise RuntimeError("YouTube scrape failed")
