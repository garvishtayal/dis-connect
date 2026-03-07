from typing import Any


# Placeholder search: returns mock photo or reel items by content_type.
async def search(query: str, content_type: str = "image") -> list[dict[str, Any]]:
    kind = "reel" if content_type == "short" else "photo"
    return [
        {"id": f"ig-{kind}-1", "type": content_type, "platform": "instagram", "url": f"https://instagram.com/p/1?q={query}", "title": f"Instagram {kind}: {query}"},
        {"id": f"ig-{kind}-2", "type": content_type, "platform": "instagram", "url": f"https://instagram.com/p/2?q={query}", "title": f"Instagram {kind} 2: {query}"},
        {"id": f"ig-{kind}-3", "type": content_type, "platform": "instagram", "url": f"https://instagram.com/p/3?q={query}", "title": f"Instagram {kind} 3: {query}"},
    ]
