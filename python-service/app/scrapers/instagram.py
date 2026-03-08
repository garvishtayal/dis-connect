"""Instagram scraper: hashtag search via instaloader; session login with up to 4 users fallback."""
import asyncio
import os
from typing import Any

import instaloader

from app.scrapers.models import IgRawItem

BASE_URL = "https://www.instagram.com"
MAX_SESSIONS = 4


def _get_session_users() -> list[str]:
    # Load up to 4 usernames from INSTAGRAM_SESSION_USERS (comma-separated).
    raw = os.getenv("INSTAGRAM_SESSION_USERS", "")
    users = [u.strip() for u in raw.split(",") if u.strip()][:MAX_SESSIONS]
    return users


def _query_to_hashtag(query: str) -> str:
    # Convert query to hashtag (no spaces, lowercased, max 30 chars).
    tag = "".join(query.split()).lower() or "explore"
    return tag[:30]


def _post_to_raw(shortcode: str, is_video: bool, caption: str | None, content_type: str) -> dict[str, Any]:
    # Build pipeline raw dict from post (shortcode, is_video, caption).
    path = "reel" if is_video else "p"
    url = f"{BASE_URL}/{path}/{shortcode}/"
    title = (caption or "Instagram post")[:500]
    item = IgRawItem(id=f"ig-{content_type}-{shortcode}", type=content_type, url=url, title=title, metadata={"shortcode": shortcode, "is_video": is_video})
    return item.to_dict()


def _search_instagram_sync(hashtag: str, content_type: str, loader: instaloader.Instaloader, max_count: int = 25) -> list[dict[str, Any]]:
    # Fetch hashtag posts; filter by image/short per content_type.
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


def _try_with_loader(hashtag: str, content_type: str, username: str | None) -> list[dict[str, Any]] | None:
    # Try search with loader (session if username else anonymous).
    loader = instaloader.Instaloader(max_connection_attempts=1)
    if username:
        try:
            loader.load_session_from_file(username)
        except Exception:
            return None
    try:
        return _search_instagram_sync(hashtag, content_type, loader)
    except Exception:
        return None


async def search(query: str, content_type: str = "image") -> list[dict[str, Any]]:
    # Search IG by hashtag; try sessions in order (up to 4), then anonymous.
    hashtag = _query_to_hashtag(query)
    users = _get_session_users()
    # Try each session first
    for username in users:
        try:
            result = await asyncio.to_thread(_try_with_loader, hashtag, content_type, username)
            if result is not None:
                return result
        except Exception:
            continue
    # Fallback: anonymous (often 403)
    try:
        result = await asyncio.to_thread(_try_with_loader, hashtag, content_type, None)
        return result or []
    except Exception:
        return []
