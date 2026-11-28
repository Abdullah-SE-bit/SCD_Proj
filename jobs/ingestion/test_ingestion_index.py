"""Chunks keep their card and go into the vector index once (M6I-001, M6I-002, DBS-002). Cards here are invented."""

import json
import re
from pathlib import Path

import pytest
from scd_ingestion.chunks import MAX_CHARS, chunks_of
from scd_ingestion.index import IndexFailed, VectorIndex

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ID = json.loads((ROOT / "contracts/schemas/dimension-score.schema.json").read_text("utf-8"))[
    "properties"]["evidence_ids"]["items"]["pattern"]


def card(text, **changes):
    return {"id": "card_ab12", "source": "github", "url": "https://example.org/a", "niche_tags": ["ci"],
            "published_at": "2026-03-02", "fetched_at": "2026-11-28T10:00:00+00:00", "text": text} | changes


def test_short_cards_are_one_chunk_that_carries_the_filters():
    [chunk] = chunks_of(card("Linkly checks links."))
    assert chunk == {"chunk_id": "card_ab12#c0", "card_id": "card_ab12", "text": "Linkly checks links.",
                     "date": "2026-03-02", "source": "github", "niche": ["ci"], "url": "https://example.org/a"}
    assert re.match(EVIDENCE_ID, chunk["chunk_id"])
    assert chunks_of(card("x", published_at=None))[0]["date"] == "2026-11-28"


def test_long_text_splits_at_sentences_without_losing_any():
    text = " ".join(f"Sentence number {n} says something about links." for n in range(80))
    chunks = chunks_of(card(text))
    assert len(chunks) > 1 and all(len(c["text"]) <= MAX_CHARS for c in chunks)
    assert " ".join(c["text"] for c in chunks) == text
    assert [c["chunk_id"] for c in chunks] == [f"card_ab12#c{n}" for n in range(len(chunks))]


def test_a_sentence_longer_than_a_chunk_is_cut_not_dropped():
    text = "a" * (MAX_CHARS * 2 + 5)
    assert "".join(c["text"] for c in chunks_of(card(text))) == text


class FakeQdrant:
    def __init__(self):
        self.collections, self.points, self.calls = set(), {}, []

    def __call__(self, method, url, body=None):
        self.calls.append((method, url))
        name = url.split("/collections/")[1].split("/")[0].split("?")[0]
        if method == "GET":
            return (200, {}) if name in self.collections else (404, {})
        if url.endswith("/collections/" + name):
            self.collections.add(name)
        else:
            self.points.update({p["id"]: p for p in body["points"]})
        return 200, {"result": True}


def embed(texts):
    return [[float(len(t)), 1.0] for t in texts]


def test_indexing_creates_the_collection_once_and_a_rerun_adds_no_points():
    qdrant = FakeQdrant()
    index = VectorIndex("http://qdrant:6333", embed, size=2, send=qdrant, batch=2)
    chunks = [c for n in range(3) for c in chunks_of(card(f"Text {n}.", id=f"card_{n}"))]
    assert index.add(chunks) == 3
    index.add(chunks)
    assert len(qdrant.points) == 3
    creations = [call for call in qdrant.calls if call == ("PUT", "http://qdrant:6333/collections/chunks")]
    assert len(creations) == 1
    point = next(iter(qdrant.points.values()))
    assert point["payload"]["chunk_id"] == "card_0#c0" and point["vector"] == [7.0, 1.0]


def test_wrong_vector_size_or_a_refusal_stops_the_run():
    index = VectorIndex("http://qdrant:6333", embed, size=3, send=FakeQdrant())
    with pytest.raises(IndexFailed, match="size"):
        index.add(chunks_of(card("x")))
    refusing = VectorIndex("http://qdrant:6333", embed, size=2, send=lambda *_: (500, {}))
    with pytest.raises(IndexFailed, match="500"):
        refusing.add(chunks_of(card("x")))
