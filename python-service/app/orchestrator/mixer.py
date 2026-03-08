from collections import defaultdict
from typing import Sequence

from app.models.content import ContentItem

# Ratio: 50% Pinterest images, 40% YouTube shorts, 10% YouTube videos (of TARGET_ITEMS=40).
TARGET_ITEMS = 40
IMAGE_TOTAL = 20   # 50%
SHORT_TOTAL = 16   # 40%
VIDEO_TOTAL = 4    # 10%


# Mixes items by ratio; cap at limit so final slice keeps same mix (not all pinterest when limit < 40).
def mix_by_ratio(items: Sequence[ContentItem], limit: int = TARGET_ITEMS) -> list[ContentItem]:
    by_type: dict[str, list[ContentItem]] = defaultdict(list)
    for item in items:
        by_type[item.type].append(item)
    n_img = min(IMAGE_TOTAL, max(0, int(limit * 0.5)))
    n_short = min(SHORT_TOTAL, max(0, int(limit * 0.4)))
    n_vid = min(VIDEO_TOTAL, max(0, limit - n_img - n_short))
    if n_vid < 0:
        n_vid = 0
    result: list[ContentItem] = []
    images = sorted(by_type.get("image", []), key=lambda x: x.score, reverse=True)
    by_platform_img: dict[str, list[ContentItem]] = defaultdict(list)
    for it in images:
        by_platform_img[it.platform].append(it)
    result.extend(by_platform_img.get("pinterest", [])[:n_img])
    shorts = sorted(by_type.get("short", []), key=lambda x: x.score, reverse=True)
    by_platform_short: dict[str, list[ContentItem]] = defaultdict(list)
    for it in shorts:
        by_platform_short[it.platform].append(it)
    result.extend(by_platform_short.get("youtube", [])[:n_short])
    videos = sorted(by_type.get("video", []), key=lambda x: x.score, reverse=True)
    by_platform_vid: dict[str, list[ContentItem]] = defaultdict(list)
    for it in videos:
        by_platform_vid[it.platform].append(it)
    result.extend(by_platform_vid.get("youtube", [])[:n_vid])
    return result
