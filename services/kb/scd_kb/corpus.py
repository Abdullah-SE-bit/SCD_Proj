"""The indexed chunks (Qdrant) joined with their cards (PostgreSQL). A chunk without a card is never returned.

Retrieved text is data: it is quoted, never interpreted.
"""

import importlib
import json
import time
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote, urlsplit

REFRESH = 300.0  # seconds the chunk list is reused
Send = Callable[[str, Any], Any]


class Unavailable(RuntimeError):
    """A store could not be reached."""


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    card_id: str
    text: str
    date: str
    source: str
    niche: list[str]
    url: str
    retrieved_at: str


def post(url: str, body: Any) -> Any:
    if not url.startswith(("http://", "https://")):
        raise Unavailable("the vector store address starts with http:// or https://")
    request = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
            return json.load(response)["result"]
    except (OSError, ValueError, KeyError) as error:
        raise Unavailable(f"vector store: {type(error).__name__}") from error


def fetched_times(url: str) -> dict[str, str]:
    """card id -> when it was retrieved, from the cards table the ingestion job writes."""
    parts = urlsplit(url)
    try:
        driver = importlib.import_module("pg8000.dbapi")
        connection = driver.connect(user=unquote(parts.username or ""), password=unquote(parts.password or ""),
                                    host=parts.hostname, port=parts.port or 5432, database=parts.path.lstrip("/"))
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, document FROM cards")
            return {row[0]: json.loads(row[1])["fetched_at"] for row in cursor.fetchall()}
        finally:
            connection.close()
    except Exception as error:  # any driver or network error
        raise Unavailable(f"card store: {type(error).__name__}") from error


def qdrant_filter(filters: dict[str, str]) -> dict[str, Any]:
    must: list[dict[str, Any]] = [{"key": key, "match": {"value": filters[key]}}
                                  for key in ("source", "niche") if key in filters]
    dates = {bound: filters[name] for name, bound in (("date_from", "gte"), ("date_to", "lte")) if name in filters}
    if dates:
        must.append({"key": "date", "range": dates})
    return {"must": must}


class Corpus:
    """ponytail: the whole chunk list is held in memory for the word search; fine for thousands of chunks, use the
    vector store's sparse index beyond that."""

    def __init__(self, vector_url: str, cards: Callable[[], dict[str, str]], send: Send = post,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.url = f"{vector_url.rstrip('/')}/collections/chunks/points"
        self.cards, self.send, self.clock = cards, send, clock
        self.held: list[Chunk] = []
        self.by_id: dict[str, Chunk] = {}
        self.loaded: float | None = None

    def chunks(self) -> list[Chunk]:
        if self.loaded is None or self.clock() - self.loaded > REFRESH:
            fetched, offset = self.cards(), None
            found: list[dict[str, Any]] = []
            while True:
                body = {"limit": 500, "with_payload": True} | ({"offset": offset} if offset else {})
                page = self.send(f"{self.url}/scroll", body)
                found.extend(point["payload"] for point in page["points"])
                offset = page.get("next_page_offset")
                if not offset:
                    break
            self.held = [Chunk(retrieved_at=fetched[p["card_id"]], **p) for p in found if p["card_id"] in fetched]
            self.by_id = {chunk.chunk_id: chunk for chunk in self.held}
            self.loaded = self.clock()
        return self.held

    def nearest(self, vector: list[float], filters: dict[str, str], limit: int) -> list[Chunk]:
        self.chunks()
        body: dict[str, Any] = {"vector": vector, "limit": limit, "with_payload": True}
        if filters:
            body["filter"] = qdrant_filter({k: v for k, v in filters.items() if not k.startswith("date_")})
            if not body["filter"]["must"]:
                del body["filter"]
        if any(key.startswith("date_") for key in filters):
            body["limit"] = limit * 10  # dates are filtered below
        hits = self.send(f"{self.url}/search", body)
        ids = [hit["payload"]["chunk_id"] for hit in hits]
        found = [self.by_id[i] for i in ids if i in self.by_id]
        return [c for c in found if within(c.date, filters)][:limit]


def within(date: str, filters: dict[str, str]) -> bool:
    return filters.get("date_from", "") <= date <= filters.get("date_to", "9999-12-31")
