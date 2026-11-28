"""robots.txt, rate limits, back-off and cache (M05-001, ETH-002, DAT-001)."""

import pytest
from scd_tools import fetch, limits, policy
from tools_fakes import API, Network, ok

PAGE = "https://news.ycombinator.com/item?id=1"
SOURCES = policy.load_sources()


class Clock:
    now = 1000.0

    def __call__(self):
        return self.now


def build(*replies, clock=None):
    network, clock = Network(*replies), clock or Clock()
    return fetch.Fetcher(SOURCES, send=network.send, resolver=network.resolve, env={}, clock=clock), network, clock


def other(n):
    return API.replace("/1.json", f"/{n}.json")


def test_a_disallowed_robots_path_is_refused_without_fetching_the_page():
    fetcher, network, _ = build(ok("User-agent: *\nDisallow: /item", "text/plain"))
    with pytest.raises(policy.Refused, match="robots"):
        fetcher.fetch(PAGE)
    assert [c["target"] for c in network.calls] == ["/robots.txt"]


def test_an_allowed_robots_path_is_fetched_and_the_rules_are_cached():
    fetcher, network, clock = build(ok("User-agent: *\nDisallow: /private", "text/plain"),
                                    ok("<p>a</p>", "text/html"), ok("<p>b</p>", "text/html"))
    fetcher.fetch(PAGE)
    clock.now += 31
    fetcher.fetch(PAGE + "&p=2")
    assert [c["target"] for c in network.calls].count("/robots.txt") == 1


def test_missing_robots_allows_and_unreadable_robots_refuses():
    fetcher, _, _ = build(ok("", "text/plain", status=404), ok("<p>a</p>", "text/html"))
    assert fetcher.fetch(PAGE)["status"] == 200
    fetcher, network, _ = build(ok("", "text/plain", status=503))
    with pytest.raises(fetch.Upstream, match="robots"):
        fetcher.fetch(PAGE)
    assert len(network.calls) == 1


def test_the_minimum_interval_per_domain_is_enforced():
    fetcher, network, clock = build()
    fetcher.fetch("https://api.github.com/a")
    with pytest.raises(limits.RateLimited) as error:
        fetcher.fetch("https://api.github.com/b")
    assert 0 < error.value.retry_after <= 2 and len(network.calls) == 1
    fetcher.fetch(API)  # another domain has its own limit
    clock.now += 2
    fetcher.fetch("https://api.github.com/b")


def test_errors_back_off_longer_each_time_and_success_resets():
    fetcher, _, clock = build(ok("", status=500), ok("", status=500))
    waits = []
    for n in (1, 2):
        with pytest.raises(fetch.Upstream):
            fetcher.fetch(other(n))
        with pytest.raises(limits.RateLimited) as error:
            fetcher.fetch(other(9))
        waits.append(error.value.retry_after)
        clock.now += waits[-1]
    assert waits == [2.0, 4.0]
    fetcher.fetch(other(3))
    assert fetcher.pacer.failures == {}


def test_retry_after_is_honoured():
    fetcher, _, _ = build(ok("", status=429, **{"retry-after": "120"}))
    with pytest.raises(fetch.Upstream):
        fetcher.fetch(API)
    with pytest.raises(limits.RateLimited) as error:
        fetcher.fetch(other(2))
    assert error.value.retry_after == 120


def test_a_repeat_is_served_from_cache_until_it_expires():
    fetcher, network, clock = build(ok('{"v": 1}'), ok('{"v": 2}'))
    first, second = fetcher.fetch(API), fetcher.fetch(API)
    assert (first["cached"], second["cached"], len(network.calls)) == (False, True, 1)
    clock.now += SOURCES["cache_seconds"] + 1
    assert fetcher.fetch(API)["content"] == '{"v": 2}'


def test_failures_are_not_cached():
    fetcher, network, clock = build(ok("", status=500), ok("{}"))
    with pytest.raises(fetch.Upstream):
        fetcher.fetch(API)
    clock.now += 10
    assert fetcher.fetch(API)["cached"] is False and len(network.calls) == 2


def test_the_cache_is_bounded():
    cache = limits.Cache(100, 2)
    for key in "abc":
        cache.put(key, key)
    assert (cache.get("a"), cache.get("c")) == (None, "c")
