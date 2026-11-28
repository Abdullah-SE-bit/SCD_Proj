"""Allow-list, address checks, redirects and credentials (M05-001, API-007)."""

import pytest
from scd_tools import fetch, policy
from tools_fakes import API, Network, ok

SOURCES = policy.load_sources()


def fetcher(network, env=None, **changes):
    return fetch.Fetcher({**SOURCES, **changes}, send=network.send, resolver=network.resolve, env=env or {})


def test_an_allowed_page_is_fetched_with_a_clear_user_agent():
    network = Network(ok('{"id": 1}'))
    result = fetcher(network).fetch(API + "?print=pretty")
    assert (result["status"], result["content"]) == (200, '{"id": 1}')
    call = network.calls[0]
    assert call["target"] == "/v0/item/1.json?print=pretty" and "idea-validator" in call["headers"]["User-Agent"]


@pytest.mark.parametrize("url", [
    "https://example.com/", "http://api.github.com/", "https://api.github.com:8443/", "ftp://api.github.com/",
    "https://user:pw@api.github.com/", "https://api.github.com.evil.example/", "https://evil.example/@api.github.com",
    "https://127.0.0.1/", "https://[::1]/", "https://api.github.com/a b", "https://api.github.com:x/", "", None, 5,
])
def test_disallowed_addresses_are_refused_without_a_connection(url):
    network = Network()
    with pytest.raises(policy.Refused):
        fetcher(network).fetch(url)
    assert network.calls == []


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.5", "192.168.1.1", "169.254.169.254", "172.16.3.4",
                                     "0.0.0.0", "::1", "fd00::1", "100.64.0.1", "224.0.0.1"])
def test_an_allowed_name_pointing_inside_is_refused(address):
    network = Network(address=address)
    with pytest.raises(policy.Refused, match="non-public"):
        fetcher(network).fetch(API)
    assert network.calls == []


def test_the_checked_address_is_the_one_connected_to():
    network = Network()
    fetcher(network).fetch(API)
    assert network.calls[0]["address"] == network.address


def test_a_redirect_outside_the_allow_list_is_refused():
    network = Network(ok("", status=302, location="https://example.com/steal"))
    with pytest.raises(policy.Refused):
        fetcher(network).fetch(API)
    assert len(network.calls) == 1


def test_a_relative_redirect_is_followed_and_loops_end():
    network = Network(ok("", status=301, location="/v0/item/2.json"), ok("{}"))
    assert fetcher(network).fetch(API)["url"].endswith("/v0/item/2.json")
    loop = Network(*[ok("", status=302, location=API)] * 9)
    with pytest.raises(fetch.Upstream, match="redirects"):
        fetcher(loop).fetch(API)


def test_a_token_goes_only_to_its_own_domain():
    env = {"GITHUB_API_TOKEN": "test-token"}
    network = Network(ok("", status=302, location=API), ok("{}"))
    fetcher(network, env=env).fetch("https://api.github.com/repos")
    assert network.calls[0]["headers"]["Authorization"] == "Bearer test-token"
    assert "Authorization" not in network.calls[1]["headers"]


def test_post_only_where_allowed():
    network = Network(ok("{}"))
    fetcher(network).fetch("https://api.producthunt.com/v2/api/graphql", "POST", {"query": "{}"})
    assert network.calls[0]["body"] == b'{"query": "{}"}'
    for method in ("POST", "DELETE"):
        with pytest.raises(policy.Refused):
            fetcher(Network()).fetch(API, method, {})


@pytest.mark.parametrize("reply, word", [
    (ok("{}", status=500), "500"), (ok("x" * 20), "too large"), (ok("x", content_type="image/png"), "content type"),
    (ConnectionError("hacker-news.firebaseio.com: TimeoutError"), "TimeoutError"),
])
def test_unusable_answers_are_reported(reply, word):
    with pytest.raises(fetch.Upstream, match=word):
        fetcher(Network(reply), max_bytes=10).fetch(API)


def test_every_source_records_its_permission_basis():
    assert all(rules["basis"] and rules["min_interval"] >= 0 for rules in SOURCES["domains"].values())
