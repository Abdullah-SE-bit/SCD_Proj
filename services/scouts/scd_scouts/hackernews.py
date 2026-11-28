"""Hacker News through its official API (github.com/HackerNews/API)."""

import datetime
from collections.abc import Iterator
from typing import Any

from scd_scouts.client import SourceError, Tools
from scd_scouts.items import item

API = "https://hacker-news.firebaseio.com/v0"
LISTS = ("showstories", "askstories", "beststories", "topstories")


def to_item(story: Any) -> dict[str, Any] | None:
    if not isinstance(story, dict) or story.get("type") != "story" or story.get("dead") or story.get("deleted"):
        return None
    created = story.get("time")
    stamp = (datetime.datetime.fromtimestamp(created, datetime.UTC).isoformat(timespec="seconds")
             if isinstance(created, int) else None)
    page = f"https://news.ycombinator.com/item?id={story.get('id')}"
    return item("hackernews", story.get("id"), story.get("url") or page, story.get("title"), story.get("text"),
                stamp, {"score": story.get("score"), "comments": story.get("descendants"), "discussion": page})


def fetch(tools: Tools, limit: int, query: str | None = None) -> Iterator[dict[str, Any]]:
    """Up to `limit` stories from the Show, Ask, best and top lists. `query` keeps titles containing it."""
    seen: set[int] = set()
    failures = found = 0
    for name in LISTS:
        for number in tools.get_json(f"{API}/{name}.json") or []:
            if found >= limit:
                return
            if number in seen or not isinstance(number, int):
                continue
            seen.add(number)
            try:
                result = to_item(tools.get_json(f"{API}/item/{number}.json"))
            except SourceError:
                failures += 1
                if failures > 20:  # the source is failing, not one story
                    raise
                continue
            if result and (not query or query.lower() in result["title"].lower()):
                found += 1
                yield result
