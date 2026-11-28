"""Comparing two ideas on all six dimensions (USR-009)."""

import pytest
from test_profile_history import VERDICT, call, database, idea, user  # noqa: F401  (pytest fixture)


def judged(owner, title, verdict):
    idea_id = idea(owner, title)
    assert call("POST", f"/users/{owner}/ideas/{idea_id}/versions/1/verdict", verdict)[0] == 201
    return idea_id


def test_two_ideas_side_by_side_on_all_six_dimensions(database):  # noqa: F811
    owner = user("a@example.org")
    first = judged(owner, "Planner", VERDICT)
    partial = VERDICT | {"verdict": "INSUFFICIENT_EVIDENCE", "scores": VERDICT["scores"][:2]}
    second = judged(owner, "Tracker", partial)
    status, result = call("POST", f"/users/{owner}/compare", {"ideas": [first, second]})
    assert status == 200 and len(result["dimensions"]) == 6
    left, right = result["ideas"]
    assert (left["title"], left["verdict"]["verdict"], right["title"]) == ("Planner", "GO", "Tracker")
    assert left["dimensions"]["learning"] == 4.5 and right["dimensions"]["learning"] is None
    assert right["dimensions"]["competition"] == 2.0


def test_an_unjudged_idea_has_empty_columns(database):  # noqa: F811
    owner = user("a@example.org")
    pair = [idea(owner, "one"), idea(owner, "two")]
    result = call("POST", f"/users/{owner}/compare", {"ideas": pair})[1]
    assert result["ideas"][0]["verdict"] is None and set(result["ideas"][0]["dimensions"].values()) == {None}


@pytest.mark.parametrize("pick", [lambda a, b: [a], lambda a, b: [a, a], lambda a, b: [a, b, a], lambda a, b: "ab",
                                  lambda a, b: [a, 5]])
def test_bad_choices(database, pick):  # noqa: F811
    owner = user("a@example.org")
    pair = idea(owner, "one"), idea(owner, "two")
    assert call("POST", f"/users/{owner}/compare", {"ideas": pick(*pair)})[0] == 400


def test_another_users_idea_cannot_be_compared(database):  # noqa: F811
    owner, other = user("a@example.org"), user("b@example.org")
    theirs, mine = idea(owner), idea(other)
    assert call("POST", f"/users/{other}/compare", {"ideas": [mine, theirs]})[0] == 404
