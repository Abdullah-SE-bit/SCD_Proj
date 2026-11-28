"""The GitHub connector (M04-001, M04-003)."""

from scd_scouts import github
from scouts_fakes import FakeTools


def repo(number, **extra):
    return {"id": number, "full_name": f"o/r{number}", "html_url": f"https://github.com/o/r{number}",
            "description": "A thing", "stargazers_count": number, "topics": ["education"], **extra}


def test_repositories_become_items_without_owners():
    tools = FakeTools({"search/repositories": {"items": [repo(1, owner={"login": "person"})]}})
    result = list(github.fetch(tools, 10, "planner"))
    assert result[0]["signals"]["stars"] == 1 and "person" not in str(result)
    assert "q=planner" in tools.requests[0]["url"] and "per_page=100" in tools.requests[0]["url"]


def test_private_and_forked_repositories_are_skipped():
    tools = FakeTools({"search": {"items": [repo(1, private=True), repo(2, fork=True), repo(3)]}})
    assert [i["external_id"] for i in github.fetch(tools, 10, "x")] == ["3"]


def test_the_limit_is_shared_across_topics_with_a_pause_between_searches():
    pages = {f"topic%3A{topic}&": {"items": [repo(n * 100 + i) for i in range(5)]}
             for n, topic in enumerate(github.TOPICS)}
    tools = FakeTools(pages)
    result = list(github.fetch(tools, len(github.TOPICS) * 2))
    assert len(result) == len(github.TOPICS) * 2 and len(tools.requests) == len(github.TOPICS)
    assert tools.pauses == [github.PAUSE_SECONDS] * (len(github.TOPICS) - 1)


def test_pages_are_followed_until_the_share_is_met():
    tools = FakeTools({"&page=1": {"items": [repo(i) for i in range(100)]},
                       "&page=2": {"items": [repo(i) for i in range(100, 130)]}})
    assert len(list(github.fetch(tools, 120, "x"))) == 120
    assert len(tools.requests) == 2
