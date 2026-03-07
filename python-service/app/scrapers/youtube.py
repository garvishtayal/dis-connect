from typing import Any


# Placeholder search: returns mock short or video items by content_type.
async def search(query: str, content_type: str = "video") -> list[dict[str, Any]]:
    kind = "shorts" if content_type == "short" else "video"
    return [
        {"id": f"yt-{kind}-1", "type": content_type, "platform": "youtube", "url": f"https://youtube.com/{kind}/1?q={query}", "title": f"YouTube {kind}: {query}"},
        {"id": f"yt-{kind}-2", "type": content_type, "platform": "youtube", "url": f"https://youtube.com/{kind}/2?q={query}", "title": f"YouTube {kind} 2: {query}"},
        {"id": f"yt-{kind}-3", "type": content_type, "platform": "youtube", "url": f"https://youtube.com/{kind}/3?q={query}", "title": f"YouTube {kind} 3: {query}"},
    ]
