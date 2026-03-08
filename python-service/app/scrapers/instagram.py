"""Instagram scraper: hashtag search via instaloader; fetch then separate images vs reels; up to 4 session fallback."""
import asyncio
import os
from typing import Any

import instaloader

from app.scrapers.models import IgRawItem

BASE_URL = "https://www.instagram.com"
MAX_SESSIONS = 4
MAX_POSTS = 30


# LLM returns hashtag directly; normalize to tag name (strip #, lower, max 30).
def _normalize_hashtag(query: str) -> str:
    tag = (query or "").strip().lstrip("#").replace(" ", "").lower() or "explore"
    return tag[:30]


# Load up to 4 usernames from INSTAGRAM_SESSION_USERS (comma-separated).
def _get_session_users() -> list[str]:
    raw = os.getenv("INSTAGRAM_SESSION_USERS", "")
    return [u.strip() for u in raw.split(",") if u.strip()][:MAX_SESSIONS]


# Build pipeline raw dict; type = short for reels, image for photos.
def _post_to_raw(shortcode: str, is_video: bool, caption: str | None) -> dict[str, Any]:
    content_type = "short" if is_video else "image"
    path = "reel" if is_video else "p"
    url = f"{BASE_URL}/{path}/{shortcode}/"
    title = (caption or "Instagram post")[:500]
    item = IgRawItem(id=f"ig-{content_type}-{shortcode}", type=content_type, url=url, title=title, metadata={"shortcode": shortcode, "is_video": is_video})
    return item.to_dict()


# Fetch hashtag posts; keep only images (GraphImage/Sidecar) and reels (GraphReel), exclude feed videos (GraphVideo).
def _fetch_hashtag_posts(hashtag: str, loader: instaloader.Instaloader) -> list[dict[str, Any]]:
    try:
        tag = instaloader.Hashtag.from_name(loader.context, hashtag)
    except Exception:
        return []
    results: list[dict[str, Any]] = []
    for post in tag.get_posts():
        if len(results) >= MAX_POSTS:
            break
        shortcode = getattr(post, "shortcode", None) or ""
        if not shortcode:
            continue
        typename = getattr(post, "typename", "") or ""
        if typename == "GraphVideo":
            continue
        is_video = typename == "GraphReel"
        caption = getattr(post, "caption", None) or ""
        results.append(_post_to_raw(shortcode, is_video, caption))
    return results


# Try fetch with one loader (session if username else anonymous).
def _try_with_loader(hashtag: str, username: str | None) -> list[dict[str, Any]] | None:
    loader = instaloader.Instaloader(max_connection_attempts=1)
    if username:
        try:
            loader.load_session_from_file(username)
        except Exception:
            return None
    try:
        return _fetch_hashtag_posts(hashtag, loader)
    except Exception:
        return None


# Search by hashtag (query from LLM); try sessions then anonymous; return images + reels.
async def search(query: str) -> list[dict[str, Any]]:
    hashtag = _normalize_hashtag(query)
    users = _get_session_users()
    for username in users:
        try:
            result = await asyncio.to_thread(_try_with_loader, hashtag, username)
            if result is not None:
                return result
        except Exception:
            continue
    try:
        result = await asyncio.to_thread(_try_with_loader, hashtag, None)
        return result or []
    except Exception:
        return []
