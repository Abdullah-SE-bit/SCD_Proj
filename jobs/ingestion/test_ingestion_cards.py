"""Scout items become idea cards, once each (M6I-001, M6I-002, SCH-001, ETH-003). Items here are invented."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from scd_ingestion.cards import canonical_url, card_from, new_cards

SCHEMA = json.loads((Path(__file__).resolve().parents[2] / "contracts/schemas/idea-card.schema.json")
                    .read_text("utf-8"))


def item(**changes):
    return {"source": "hackernews", "external_id": "1", "url": "https://example.org/app", "title": "Show HN: Linkly",
            "text": "<p>Linkly checks README links.</p> <p>It runs in CI &amp; locally.</p>",
            "created_at": "2026-03-02T10:00:00+00:00", "signals": {"score": 3},
            "retrieved_at": "2026-11-28T10:00:00+00:00"} | changes


def test_a_card_follows_the_contract_and_invents_nothing():
    card = card_from(item(signals={"topics": ["Developer Tools", "ci"]}))
    Draft202012Validator(SCHEMA).validate(card)
    assert card["name"] == "Linkly"
    assert card["summary"] == "Linkly checks README links."
    assert card["text"] == "Linkly. Linkly checks README links. It runs in CI & locally."
    assert card["niche_tags"] == ["developer-tools", "ci"]
    assert card["published_at"] == "2026-03-02"
    # nothing the source did not say
    assert (card["problem"], card["customer"], card["stage"], card["funding_usd"]) == ("", "", "unknown", None)
    assert "signals" not in card and "external_id" not in card


def test_a_title_alone_is_enough():
    card = card_from(item(text="", title="owner/tool", created_at=None))
    Draft202012Validator(SCHEMA).validate(card)
    assert (card["summary"], card["text"], card["published_at"]) == ("owner/tool", "owner/tool", None)


@pytest.mark.parametrize("bad", [{"url": "ftp://x"}, {"title": "  "}, {"source": ""}, {"retrieved_at": None},
                                 {"title": "<p></p>"}])
def test_unusable_items_are_skipped(bad):
    assert card_from(item(**bad)) is None


@pytest.mark.parametrize("url", [
    "http://www.Example.org/app/", "https://example.org/app?utm_source=hn&ref=x#top", "https://EXAMPLE.org/app"])
def test_the_same_page_has_one_address(url):
    assert canonical_url(url) == "https://example.org/app"


def test_queries_that_select_a_page_are_kept():
    assert canonical_url("https://news.ycombinator.com/item?id=2&utm_medium=x") == (
        "https://news.ycombinator.com/item?id=2")
    assert canonical_url("https://example.org/a?b=2&a=1") == canonical_url("https://example.org/a?a=1&b=2")


def test_duplicates_by_address_or_content_are_dropped_and_a_rerun_adds_nothing():
    items = [item(), item(url="http://www.example.org/app/?utm_source=x", external_id="2"),
             item(url="https://mirror.example.net/copy", external_id="3"),
             item(url="https://example.org/other", title="Other", text="Something else.")]
    first = new_cards(items, known=[])
    assert [c["url"] for c in first] == ["https://example.org/app", "https://example.org/other"]
    assert new_cards(items, known=first) == []


def test_the_id_depends_only_on_the_address():
    assert card_from(item())["id"] == card_from(item(title="Renamed", text="new"))["id"]
    assert card_from(item())["id"].startswith("card_")
