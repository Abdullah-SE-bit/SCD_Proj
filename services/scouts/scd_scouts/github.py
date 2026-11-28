"""Public repositories through the official GitHub REST search API."""

import os
from collections.abc import Callable, Iterator
from typing import Any
from urllib.parse import urlencode

from scd_scouts.client import Tools
from scd_scouts.items import item

API = "https://api.github.com/search/repositories"
TOPICS = ("education", "productivity", "developer-tools", "study-planner", "health", "fintech", "accessibility",
          "sustainability", "student", "automation", "chatbot", "data-visualization", "e-commerce", "travel",
          "note-taking", "job-search")
PER_PAGE = 100
# GitHub allows 10 searches a minute without a token and 30 with one (the token itself is held by M5)
PAUSE_SECONDS = float(os.environ.get("GITHUB_PAUSE_SECONDS", "6.5"))


def to_item(repository: Any) -> dict[str, Any] | None:
    if not isinstance(repository, dict) or repository.get("private") or repository.get("fork"):
        return None
    return item("github", repository.get("id"), repository.get("html_url"), repository.get("full_name"),
                repository.get("description"), repository.get("created_at"),
                {"stars": repository.get("stargazers_count"), "forks": repository.get("forks_count"),
                 "language": repository.get("language"), "topics": repository.get("topics"),
                 "pushed_at": repository.get("pushed_at")})


def fetch(tools: Tools, limit: int, query: str | None = None,
          sleep: Callable[[float], None] | None = None) -> Iterator[dict[str, Any]]:
    """The most starred repositories of each topic (or of one query), spread so no topic fills the limit."""
    searches = [query] if query else [f"topic:{topic}" for topic in TOPICS]
    share = max(1, -(-limit // len(searches)))
    pause = sleep or tools.sleep
    seen: set[str] = set()
    for index, search in enumerate(searches):
        taken, page = 0, 1
        while taken < share and len(seen) < limit and page <= 10:  # the API stops at 1000 results
            if index or page > 1:
                pause(PAUSE_SECONDS)
            address = f"{API}?{urlencode({'q': search, 'sort': 'stars', 'per_page': PER_PAGE, 'page': page})}"
            found = (tools.get_json(address) or {}).get("items") or []
            for repository in found:
                result = to_item(repository)
                if result and result["external_id"] not in seen and taken < share and len(seen) < limit:
                    seen.add(result["external_id"])
                    taken += 1
                    yield result
            if len(found) < PER_PAGE:
                break
            page += 1
