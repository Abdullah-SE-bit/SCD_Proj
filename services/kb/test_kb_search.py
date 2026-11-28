"""M6 search: hybrid ranking with reranking, filters, citations, freshness and coverage (M06-001 to M06-005,
API-008, SCH-003). The chunks here are invented."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from scd_kb import app, search
from scd_kb.corpus import Chunk, Unavailable

SCHEMA = json.loads((Path(__file__).resolve().parents[2] / "contracts/schemas/evidence-item.schema.json")
                    .read_text("utf-8"))


def chunk(n, text, source="github", date="2026-03-01", niche=("ci",)):
    return Chunk(chunk_id=f"card_{n}#c0", card_id=f"card_{n}", text=text, date=date, source=source,
                 niche=list(niche), url=f"https://example.org/{n}", retrieved_at="2026-11-28T10:00:00+00:00")


CHUNKS = [chunk(1, "Checks broken links in README files"),
          chunk(2, "Pomodoro timer for students", source="hackernews", date="2026-05-01", niche=("education",)),
          chunk(3, "Link checker for printed posters", date="2025-01-15"),
          chunk(4, "Recipe sharing for flatmates", source="hackernews", niche=())]


class Corpus:
    def __init__(self, chunks=CHUNKS, nearest=("card_3#c0", "card_1#c0")):
        self.all, self.order, self.filters = list(chunks), list(nearest), None

    def chunks(self):
        return self.all

    def nearest(self, vector, filters, limit):
        self.filters = filters
        return [c for i in self.order for c in self.all if c.chunk_id == i and search.allowed(c, filters)][:limit]


def engine(corpus=None, scores=None):
    corpus = corpus or Corpus()
    rerank = scores or (lambda query, texts: [float("link" in t.lower()) for t in texts])
    return search.Search(corpus, embed=lambda query: [1.0], rerank=rerank)


def test_results_are_evidence_items_that_cite_their_card():
    items = engine().query("broken link checker")
    assert [i["card_id"] for i in items][:2] == ["card_3", "card_1"] or [i["card_id"] for i in items][:2] == [
        "card_1", "card_3"]
    for item in items:
        Draft202012Validator(SCHEMA).validate(item)
        assert item["evidence_id"].startswith(item["card_id"] + "#c")
        assert item["url"].startswith("https://") and item["retrieved_at"] == "2026-11-28T10:00:00+00:00"


def test_words_find_what_the_vectors_miss():
    corpus = Corpus(nearest=())  # the dense side returns nothing
    assert [i["card_id"] for i in engine(corpus).query("pomodoro timer")][0] == "card_2"


def test_vectors_find_what_the_words_miss():
    corpus = Corpus(nearest=("card_4#c0",))
    assert [i["card_id"] for i in engine(corpus, scores=lambda q, t: [0.0] * len(t)).query("cooking")] == ["card_4"]


def test_the_reranker_decides_the_final_order():
    order = {"Recipe sharing for flatmates": 9.0}
    items = engine(Corpus(nearest=("card_1#c0", "card_4#c0")),
                   scores=lambda q, texts: [order.get(t, 0.0) for t in texts]).query("links")
    assert items[0]["card_id"] == "card_4"


@pytest.mark.parametrize("filters, cards", [
    ({"source": "hackernews"}, {"card_2", "card_4"}),
    ({"niche": "education"}, {"card_2"}),
    ({"date_from": "2026-04-01"}, {"card_2"}),
    ({"date_to": "2025-12-31"}, {"card_3"}),
    ({"date_from": "2026-03-01", "date_to": "2026-03-01"}, {"card_1", "card_4"}),
])
def test_each_filter_limits_both_sides(filters, cards):
    corpus = Corpus(nearest=[c.chunk_id for c in CHUNKS])
    found = engine(corpus).query("link timer recipe students flatmates posters README", filters)
    assert {i["card_id"] for i in found} == cards


def test_no_match_is_an_explicit_empty_list():
    assert engine(Corpus(nearest=())).query("zzzz", {"source": "producthunt"}) == []


def test_coverage_reports_counts_and_freshness():
    assert search.coverage(CHUNKS) == {
        "cards": 4, "chunks": 4, "by_source": {"github": 2, "hackernews": 2},
        "published": {"oldest": "2025-01-15", "newest": "2026-05-01"},
        "last_retrieved": "2026-11-28T10:00:00+00:00", "niches": 2, "cards_without_niche": 1}
    assert search.coverage([])["cards"] == 0


def call(body, monkeypatch, fake=None):
    monkeypatch.setattr(app, "engine", fake or engine())
    return app.service.handle("POST", "/search", json.dumps(body).encode())


def test_the_route_answers_with_the_items(monkeypatch):
    status, items = call({"query": "link checker", "filters": {"source": "github"}}, monkeypatch)
    assert status == 200 and {i["source"] for i in items} == {"github"}


@pytest.mark.parametrize("body", [
    {}, {"query": ""}, {"query": "   "}, {"query": 5}, {"query": "x" * 501}, {"query": "x", "filters": []},
    {"query": "x", "filters": {"author": "a"}}, {"query": "x", "filters": {"date_from": "01-01-2026"}},
    {"query": "x", "filters": {"date_to": "2026-13-01"}}, {"query": "x", "filters": {"source": ""}}])
def test_the_route_rejects_bad_requests(monkeypatch, body):
    assert call(body, monkeypatch)[0] == 400


def test_a_store_that_is_down_or_absent_is_reported(monkeypatch):
    class Down(Corpus):
        def chunks(self):
            raise Unavailable("no route")

    assert call({"query": "x"}, monkeypatch, engine(Down()))[0] == 503
    monkeypatch.setattr(app, "engine", None)
    assert app.service.handle("POST", "/search", b'{"query": "x"}')[0] == 503
    assert app.service.handle("GET", "/coverage")[0] == 503
