from typing import Any


# Placeholder search: returns mock image items for the query.
async def search(query: str) -> list[dict[str, Any]]:
    return [
        {"id": "pin-1", "type": "image", "platform": "pinterest", "url": f"https://pinterest.com/pin/1?q={query}", "title": f"Pinterest: {query}"},
        {"id": "pin-2", "type": "image", "platform": "pinterest", "url": f"https://pinterest.com/pin/2?q={query}", "title": f"Pinterest image 2: {query}"},
        {"id": "pin-3", "type": "image", "platform": "pinterest", "url": f"https://pinterest.com/pin/3?q={query}", "title": f"Pinterest image 3: {query}"},
    ]
