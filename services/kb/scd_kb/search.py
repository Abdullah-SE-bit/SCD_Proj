"""Hybrid search: word ranking (BM25) and vector ranking fused by rank, then reranked by a cross-encoder."""

import math
import re
from collections import Counter
from collections.abc import Callable
from typing import Any

from scd_kb.corpus import Chunk, within

CANDIDATES, RESULTS = 30, 10
K1, B, RRF = 1.5, 0.75, 60
Embed = Callable[[str], list[float]]
Rerank = Callable[[str, list[str]], list[float]]


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def allowed(chunk: Chunk, filters: dict[str, str]) -> bool:
    return (filters.get("source", chunk.source) == chunk.source
            and ("niche" not in filters or filters["niche"] in chunk.niche) and within(chunk.date, filters))


def by_words(query: str, chunks: list[Chunk], limit: int) -> list[Chunk]:
    """BM25 over the given chunks; only chunks sharing a word with the query."""
    documents = [Counter(words(c.text)) for c in chunks]
    if not documents:
        return []
    average = sum(sum(d.values()) for d in documents) / len(documents) or 1
    terms = set(words(query))
    rarity = {t: math.log(1 + (len(documents) - n + 0.5) / (n + 0.5))
              for t in terms for n in [sum(1 for d in documents if t in d)]}
    scored = []
    for chunk, document in zip(chunks, documents, strict=True):
        length = sum(document.values())
        score = sum(rarity[t] * document[t] * (K1 + 1) / (document[t] + K1 * (1 - B + B * length / average))
                    for t in terms if t in document)
        if score:
            scored.append((score, chunk))
    scored.sort(key=lambda pair: (-pair[0], pair[1].chunk_id))
    return [chunk for _, chunk in scored[:limit]]


def fused(*rankings: list[Chunk]) -> list[Chunk]:
    """Reciprocal rank fusion: a chunk high in either ranking comes out high."""
    scores: dict[str, float] = {}
    chunks: dict[str, Chunk] = {}
    for ranking in rankings:
        for place, chunk in enumerate(ranking):
            chunks[chunk.chunk_id] = chunk
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1 / (RRF + place + 1)
    return [chunks[i] for i in sorted(scores, key=lambda i: (-scores[i], i))]


def evidence(chunk: Chunk) -> dict[str, str]:
    return {"evidence_id": chunk.chunk_id, "card_id": chunk.card_id, "quote": chunk.text, "source": chunk.source,
            "url": chunk.url, "retrieved_at": chunk.retrieved_at}


class Search:
    def __init__(self, corpus: Any, embed: Embed, rerank: Rerank) -> None:
        self.corpus, self.embed, self.rerank = corpus, embed, rerank

    def query(self, text: str, filters: dict[str, str] | None = None, hybrid: bool = True,
              reranked: bool = True) -> list[dict[str, str]]:
        """`hybrid` and `reranked` exist so evaluation can measure what each step adds."""
        filters = filters or {}
        pool = [c for c in self.corpus.chunks() if allowed(c, filters)]
        dense = self.corpus.nearest(self.embed(text), filters, CANDIDATES) if pool else []
        candidates = fused(dense, by_words(text, pool, CANDIDATES) if hybrid else [])[:CANDIDATES]
        if reranked and candidates:
            scores = self.rerank(text, [c.text for c in candidates])
            order = sorted(range(len(candidates)), key=lambda i: (-scores[i], i))
            candidates = [candidates[i] for i in order]
        return [evidence(c) for c in candidates[:RESULTS]]


def coverage(chunks: list[Chunk]) -> dict[str, Any]:
    """What the knowledge base holds and how fresh it is (M06-005)."""
    cards = {c.card_id: c for c in chunks}
    dates = sorted(c.date for c in cards.values())
    return {"cards": len(cards), "chunks": len(chunks),
            "by_source": dict(sorted(Counter(c.source for c in cards.values()).items())),
            "published": {"oldest": dates[0] if dates else None, "newest": dates[-1] if dates else None},
            "last_retrieved": max((c.retrieved_at for c in cards.values()), default=None),
            "niches": len({n for c in cards.values() for n in c.niche}),
            "cards_without_niche": sum(1 for c in cards.values() if not c.niche)}
