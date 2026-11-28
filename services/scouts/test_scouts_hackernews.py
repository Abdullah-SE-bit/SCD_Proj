"""The M5 client, the item shape and the Hacker News connector (M04-001, M04-003, ARC-007)."""

import pytest
from scd_scouts import hackernews
from scd_scouts.client import SourceError, Tools
from scd_scouts.items import item
from scouts_fakes import Failure, FakeTools


def story(number, **extra):
    return {"id": number, "type": "story", "title": f"Show HN: Tool {number}", "time": 1_700_000_000,
            "score": 10, "descendants": 2, **extra}


def routes(*numbers, **items):
    table = {"showstories": list(numbers), "askstories": [], "beststories": [], "topstories": []}
    table.update({f"item/{n}.json": items.get(f"i{n}", story(n)) for n in numbers})
    return table


def test_every_request_goes_through_the_tool_layer():
    tools = FakeTools(routes(1))
    list(hackernews.fetch(tools, 5))
    assert tools.url == "http://tools:8000/fetch"
    assert all(r["url"].startswith("https://hacker-news.firebaseio.com/v0/") for r in tools.requests)


def test_stories_become_items_without_author_names():
    result = list(hackernews.fetch(FakeTools(routes(1, i1=story(1, by="someone", text="Why I built it"))), 5))
    assert result[0]["url"] == "https://news.ycombinator.com/item?id=1"
    assert (result[0]["source"], result[0]["external_id"], result[0]["signals"]["score"]) == ("hackernews", "1", 10)
    assert result[0]["created_at"].startswith("2023-11-14") and "someone" not in str(result)


def test_dead_deleted_comments_and_repeats_are_skipped_and_the_limit_holds():
    table = routes(1, 2, 3, 4, 5, i1=story(1, dead=True), i2={"id": 2, "type": "comment"}, i3=story(3, deleted=True))
    table["askstories"] = [4, 5]
    assert [i["external_id"] for i in hackernews.fetch(FakeTools(table), 10)] == ["4", "5"]
    assert len(list(hackernews.fetch(FakeTools(table), 1))) == 1


def test_one_broken_story_is_skipped_but_a_broken_source_stops():
    table = routes(1, 2, i1=Failure())
    assert [i["external_id"] for i in hackernews.fetch(FakeTools(table), 5)] == ["2"]
    many = {"showstories": list(range(100)), "item/": Failure()}
    with pytest.raises(SourceError):
        list(hackernews.fetch(FakeTools(many), 5))


def test_a_rate_limit_answer_is_waited_out():
    answers = [(429, {"error": "slow down", "retry_after": 2.0}), (200, {"content": "[1]"})]
    waits = []
    tools = Tools("http://tools:8000", lambda url, body: answers.pop(0), waits.append)
    assert tools.get_json("https://x") == [1] and waits == [2.05]


@pytest.mark.parametrize("answer", [
    (429, {"error": "long", "retry_after": 3600}), (403, {"error": "refused"}), (200, {"content": "<html>"}),
    (429, {"error": "no wait given"}),
])
def test_refusals_and_long_waits_are_errors(answer):
    with pytest.raises(SourceError):
        Tools("http://tools:8000", lambda url, body: answer, lambda s: None).get_json("https://x")


def test_a_limit_that_never_lifts_gives_up():
    with pytest.raises(SourceError, match="still"):
        Tools("http://t", lambda u, b: (429, {"retry_after": 1}), lambda s: None).get_json("https://x")


@pytest.mark.parametrize("bad", [
    (None, "https://a", "t"), (1, "javascript:alert(1)", "t"), (1, None, "t"), (1, "https://a", "  "),
])
def test_records_without_the_basics_are_dropped(bad):
    assert item("hackernews", *bad, "", None, {}) is None
