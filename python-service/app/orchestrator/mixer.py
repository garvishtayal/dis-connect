from collections import defaultdict
from typing import Sequence

from app.models.content import ContentItem

# Ratio targets: 8 image (Pinterest), 8 short (YouTube Shorts), 8 video (YouTube).
IMAGE_PER_PLATFORM = 8
SHORT_PER_PLATFORM = 8
VIDEO_TOTAL = 8


# Mixes items by ratio: top image, short, video (by platform).
def mix_by_ratio(items: Sequence[ContentItem]) -> list[ContentItem]:
    by_type: dict[str, list[ContentItem]] = defaultdict(list)
    for item in items:
        by_type[item.type].append(item)
    result: list[ContentItem] = []
    images = sorted(by_type.get("image", []), key=lambda x: x.score, reverse=True)
    by_platform_img: dict[str, list[ContentItem]] = defaultdict(list)
    for it in images:
        by_platform_img[it.platform].append(it)
    result.extend(by_platform_img.get("pinterest", [])[:IMAGE_PER_PLATFORM])
    shorts = sorted(by_type.get("short", []), key=lambda x: x.score, reverse=True)
    by_platform_short: dict[str, list[ContentItem]] = defaultdict(list)
    for it in shorts:
        by_platform_short[it.platform].append(it)
    result.extend(by_platform_short.get("youtube", [])[:SHORT_PER_PLATFORM])
    # Videos: 8 YouTube.
    videos = sorted(by_type.get("video", []), key=lambda x: x.score, reverse=True)
    by_platform_vid: dict[str, list[ContentItem]] = defaultdict(list)
    for it in videos:
        by_platform_vid[it.platform].append(it)
    result.extend(by_platform_vid.get("youtube", [])[:VIDEO_TOTAL])
    return result
