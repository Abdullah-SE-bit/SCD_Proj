"""The Product Hunt connector, with recorded-shape answers (M04-001)."""

import pytest
from scd_scouts import producthunt
from scd_scouts.client import SourceError
from scouts_fakes import FakeTools


def page(*numbers, more=False):
    edges = [{"node": {"id": str(n), "name": f"App {n}", "tagline": "Plan", "description": "your week",
                       "url": f"https://www.producthunt.com/posts/app-{n}", "votesCount": n,
                       "topics": {"edges": [{"node": {"name": "Productivity"}}]}}} for n in numbers]
    return {"data": {"posts": {"edges": edges, "pageInfo": {"hasNextPage": more, "endCursor": "c1"}}}}


def test_posts_become_items_through_a_post_request():
    tools = FakeTools({"graphql": page(1, 2)})
    result = list(producthunt.fetch(tools, 10))
    assert [i["text"] for i in result] == ["Plan your week"] * 2
    assert result[0]["signals"]["topics"] == ["Productivity"]
    assert tools.requests[0]["method"] == "POST" and "posts(" in tools.requests[0]["payload"]["query"]


def test_the_limit_stops_paging():
    tools = FakeTools({"graphql": page(1, 2, 3, more=True)})
    assert len(list(producthunt.fetch(tools, 2))) == 2 and len(tools.requests) == 1


def test_an_error_answer_is_a_source_error():
    with pytest.raises(SourceError, match="invalid_token"):
        list(producthunt.fetch(FakeTools({"graphql": {"errors": [{"error": "invalid_token"}]}}), 5))
