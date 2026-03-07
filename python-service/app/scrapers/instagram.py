"""Instagram scraper: hashtag search via instaloader; return photos and reels as raw dicts for pipeline."""
import asyncio
from typing import Any

import instaloader

from app.scrapers.models import IgRawItem

BASE_URL = "https://www.instagram.com"


# Converts search query to a single hashtag string (no spaces, lowercased, max 30 chars).
def _query_to_hashtag(query: str) -> str:
    tag = "".join(query.split()).lower() or "explore"
    return tag[:30]


# Builds pipeline raw dict from one IG post (shortcode, is_video, caption) via IgRawItem.
def _post_to_raw(shortcode: str, is_video: bool, caption: str | None, content_type: str) -> dict[str, Any]:
    path = "reel" if is_video else "p"
    url = f"{BASE_URL}/{path}/{shortcode}/"
    title = (caption or "Instagram post")[:500]
    item = IgRawItem(
        id=f"ig-{content_type}-{shortcode}",
        type=content_type,
        url=url,
        title=title,
        metadata={"shortcode": shortcode, "is_video": is_video},
    )
    return item.to_dict()


# Fetches hashtag posts via instaloader (sync), filters by image/short, returns raw dicts.
def _search_instagram_sync(hashtag: str, content_type: str, max_count: int = 25) -> list[dict[str, Any]]:
    loader = instaloader.Instaloader()
    try:
        tag = instaloader.Hashtag.from_name(loader.context, hashtag)
    except Exception:
        return []
    results: list[dict[str, Any]] = []
    for post in tag.get_posts():
        if len(results) >= max_count:
            break
        is_video = getattr(post, "is_video", False)
        want_short = content_type == "short"
        if (want_short and not is_video) or (not want_short and is_video):
            continue
        shortcode = getattr(post, "shortcode", None) or ""
        if not shortcode:
            continue
        caption = getattr(post, "caption", None) or ""
        results.append(_post_to_raw(shortcode, is_video, caption, content_type))
    return results


# Search IG by hashtag from query, return raw dicts for image or short per content_type (async, in thread).
async def search(query: str, content_type: str = "image") -> list[dict[str, Any]]:
    try:
        hashtag = _query_to_hashtag(query)
        return await asyncio.to_thread(_search_instagram_sync, hashtag, content_type)
    except Exception:
        return []
