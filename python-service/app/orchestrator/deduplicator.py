from typing import Any

from app.models.content import ContentItem


# Deduplicates by URL in memory (preserves order).
def deduplicate(items: list[ContentItem]) -> list[ContentItem]:
    seen: set[str] = set()
    result: list[ContentItem] = []
    for item in items:
        if item.url in seen:
            continue
        seen.add(item.url)
        result.append(item)
    return result


# Filters out raw items whose url is in the already-shown set (Redis).
def filter_already_shown_raw(raw: list[dict[str, Any]], shown_urls: set[str]) -> list[dict[str, Any]]:
    return [r for r in raw if r.get("url") not in shown_urls]


# Keeps all fresh items and allows old/shown items up to old_ratio per type.
# With old_ratio=0.5, old items are capped at the same count as fresh (50/50 max).
def allow_partial_old_raw(
    raw: list[dict[str, Any]],
    shown_urls: set[str],
    old_ratio: float = 0.4,
) -> list[dict[str, Any]]:
    by_type_fresh: dict[str, list[dict[str, Any]]] = {}
    by_type_old: dict[str, list[dict[str, Any]]] = {}

    for r in raw:
        if not isinstance(r, dict):
            continue
        t = str(r.get("type") or "unknown")
        is_old = r.get("url") in shown_urls
        target = by_type_old if is_old else by_type_fresh
        target.setdefault(t, []).append(r)

    out: list[dict[str, Any]] = []
    all_types = set(by_type_fresh.keys()) | set(by_type_old.keys())
    for t in all_types:
        fresh = by_type_fresh.get(t, [])
        old = by_type_old.get(t, [])
        out.extend(fresh)
        if not fresh:
            # Fallback: if no fresh items exist for a type, allow old items
            # so feed generation does not collapse to zero.
            out.extend(old)
            continue
        max_old = int(len(fresh) * old_ratio / (1 - old_ratio)) if old_ratio < 1 else len(old)
        # old_ratio=0.5 => max_old=len(fresh)
        out.extend(old[:max_old])

    return out

