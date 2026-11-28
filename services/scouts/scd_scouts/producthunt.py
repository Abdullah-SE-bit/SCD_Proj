"""Products through the official Product Hunt API v2 (GraphQL). Needs a developer token, which M5 holds."""

from collections.abc import Iterator
from typing import Any

from scd_scouts.client import SourceError, Tools
from scd_scouts.items import item

API = "https://api.producthunt.com/v2/api/graphql"
QUERY = ("query($after: String) { posts(first: 20, after: $after, order: VOTES) { pageInfo { hasNextPage endCursor } "
         "edges { node { id name tagline description url votesCount commentsCount createdAt "
         "topics(first: 5) { edges { node { name } } } } } } }")


def to_item(node: Any) -> dict[str, Any] | None:
    if not isinstance(node, dict):
        return None
    topics = [e.get("node", {}).get("name") for e in (node.get("topics") or {}).get("edges", [])]
    text = " ".join(part for part in (node.get("tagline"), node.get("description")) if isinstance(part, str))
    return item("producthunt", node.get("id"), node.get("url"), node.get("name"), text, node.get("createdAt"),
                {"votes": node.get("votesCount"), "comments": node.get("commentsCount"),
                 "topics": [t for t in topics if t]})


def fetch(tools: Tools, limit: int, query: str | None = None) -> Iterator[dict[str, Any]]:
    cursor, found = None, 0
    while found < limit:
        answer = tools.get_json(API, "POST", {"query": QUERY, "variables": {"after": cursor}}) or {}
        posts = (answer.get("data") or {}).get("posts")
        if not posts:
            raise SourceError(f"Product Hunt refused the query: {str(answer.get('errors'))[:200]}")
        for edge in posts.get("edges", []):
            result = to_item(edge.get("node"))
            if result and found < limit and (not query or query.lower() in result["title"].lower()):
                found += 1
                yield result
        page = posts.get("pageInfo") or {}
        cursor = page.get("endCursor")
        if not page.get("hasNextPage") or not cursor:
            return
