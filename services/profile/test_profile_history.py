"""Idea history and versions, visible to their owner only (USR-009)."""

import json
from pathlib import Path

import pytest
from scd_profile import app
from scd_profile.migrate import migrate

VERDICT = json.loads((Path(__file__).resolve().parents[2] / "contracts/schemas/examples/verdict.valid.json")
                     .read_text("utf-8"))


@pytest.fixture
def database(empty_database, monkeypatch):
    migrate(empty_database)
    monkeypatch.setattr(app, "database", empty_database)
    return empty_database


def call(method, path, body=None):
    return app.service.handle(method, path, json.dumps(body).encode() if body is not None else b"")


def user(email):
    return call("POST", "/users", {"email": email, "password": "correct horse"})[1]["user_id"]


def idea(owner, title="Planner", text="Plans a study week"):
    return call("POST", f"/users/{owner}/ideas", {"title": title, "text": text})[1]["idea_id"]


def test_ideas_and_versions_are_listed_with_their_verdicts(database):
    owner = user("a@example.org")
    planner = idea(owner)
    base = f"/users/{owner}/ideas/{planner}/versions"
    assert call("POST", base, {"text": "Narrower: exam weeks only"})[1]["version"] == 2
    assert call("POST", f"{base}/2/verdict", VERDICT)[0] == 201
    status, listed = call("GET", f"/users/{owner}/ideas")
    assert status == 200 and listed["ideas"][0]["latest_version"] == 2
    assert (listed["ideas"][0]["verdict"]["verdict"], listed["ideas"][0]["verdict"]["score"]) == ("GO", 70.5)
    history = call("GET", base)[1]["versions"]
    assert [v["version"] for v in history] == [1, 2] and history[0]["verdict"] is None
    assert history[1]["text"] == "Narrower: exam weeks only"


def test_the_newest_verdict_of_a_version_is_shown(database):
    owner = user("a@example.org")
    planner = idea(owner)
    base = f"/users/{owner}/ideas/{planner}/versions/1/verdict"
    for number in range(8):  # all within one second
        call("POST", base, VERDICT | {"score": 60 + number})
        assert call("GET", f"/users/{owner}/ideas")[1]["ideas"][0]["verdict"]["score"] == 60 + number


def test_another_user_sees_nothing_of_it(database):
    owner, other = user("a@example.org"), user("b@example.org")
    planner = idea(owner)
    assert call("GET", f"/users/{other}/ideas")[1] == {"ideas": []}
    for method, path, body in (("GET", "versions", None), ("POST", "versions", {"text": "taken over"}),
                               ("POST", "versions/1/verdict", VERDICT)):
        assert call(method, f"/users/{other}/ideas/{planner}/{path}", body)[0] == 404


@pytest.mark.parametrize("change", [{"verdict": "MAYBE"}, {"score": 101}, {"confidence": -1}, {"scores": "x"},
                                    {"scores": [{"dimension": "fame"}]},
                                    {"scores": VERDICT["scores"][:1] * 2}])
def test_a_document_that_is_not_a_verdict_is_refused(database, change):
    owner = user("a@example.org")
    planner = idea(owner)
    assert call("POST", f"/users/{owner}/ideas/{planner}/versions/1/verdict", VERDICT | change)[0] == 400


def test_unknown_versions_and_bad_ideas(database):
    owner = user("a@example.org")
    planner = idea(owner)
    assert call("POST", f"/users/{owner}/ideas/{planner}/versions/9/verdict", VERDICT)[0] == 404
    assert call("POST", f"/users/{owner}/ideas", {"title": "", "text": "x"})[0] == 400
