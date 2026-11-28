"""Public history routes need a login and never pass a crafted identifier inwards (API-006)."""

import pytest
from scd_gateway import app, tokens
from test_gateway_auth import call, profile  # noqa: F401  (pytest fixture)


def token():
    return tokens.issue("u_1", app.key)


@pytest.mark.parametrize("path", ["/ideas", "/ideas/idea_1/versions"])
def test_history_needs_a_login(profile, path):  # noqa: F811
    assert call("GET", path)[0] == 401
    assert profile.calls == []


def test_history_asks_for_the_signed_in_user_only(profile):  # noqa: F811
    assert call("GET", "/ideas", token=token())[0] == 200
    assert call("GET", "/ideas/idea_1/versions", token=token())[0] == 200
    assert [c[1] for c in profile.calls] == ["/users/u_1/ideas", "/users/u_1/ideas/idea_1/versions"]


@pytest.mark.parametrize("idea_id", ["..", "a%2Fb", "x" * 81, "a b"])
def test_a_crafted_identifier_is_not_forwarded(profile, idea_id):  # noqa: F811
    assert call("GET", f"/ideas/{idea_id}/versions", token=token())[0] == 404
    assert profile.calls == []


def test_compare_forwards_the_two_ideas(profile):  # noqa: F811
    assert call("GET", "/compare?a=idea_1&b=idea_2", token=token())[0] == 200
    assert profile.calls == [("POST", "/users/u_1/compare", {"ideas": ["idea_1", "idea_2"]})]


@pytest.mark.parametrize("query", ["", "?a=idea_1", "?a=idea_1&b=idea_1", "?a=..&b=idea_2", "?a=x%2Fy&b=idea_2"])
def test_bad_comparisons_are_not_forwarded(profile, query):  # noqa: F811
    assert call("GET", f"/compare{query}", token=token())[0] == 400
    assert profile.calls == []


def test_compare_needs_a_login_and_ignores_a_forged_query_header(profile):  # noqa: F811
    assert call("GET", "/compare?a=idea_1&b=idea_2")[0] == 401
    headers = {"Authorization": f"Bearer {token()}", "X-Query": "a=idea_1&b=idea_2"}
    assert app.service.handle("GET", "/compare", b"", headers)[0] == 400


def test_metrics_show_the_cache_counts(profile):  # noqa: F811
    profile.answers["/metrics"] = (200, {"cache_hits": 3})
    assert call("GET", "/metrics") == (200, {"cache": {"cache_hits": 3}})
