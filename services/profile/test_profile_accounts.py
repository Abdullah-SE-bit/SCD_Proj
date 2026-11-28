"""M2 internal account and profile routes (API-003, M01-003, SCH-002)."""

import json
from pathlib import Path

import pytest
from scd_profile import app, passwords
from scd_profile import repositories as repo
from scd_profile.migrate import migrate

PROFILE = json.loads((Path(__file__).resolve().parents[2] / "contracts/schemas/examples/student-profile.valid.json")
                     .read_text("utf-8"))
GOOD = {"email": "Student@Example.org ", "password": "correct horse"}


@pytest.fixture
def database(empty_database, monkeypatch):
    migrate(empty_database)
    monkeypatch.setattr(app, "database", empty_database)
    return empty_database


def call(method, path, body=None):
    return app.service.handle(method, path, json.dumps(body).encode() if body is not None else b"")


def test_passwords_are_salted_hashes_that_verify():
    first, second = passwords.hashed("correct horse"), passwords.hashed("correct horse")
    assert first != second and "correct horse" not in first
    assert passwords.matches("correct horse", first)
    assert not passwords.matches("wrong horse", first)
    assert not passwords.matches("correct horse", "not-a-hash")


def test_register_then_log_in(database):
    status, body = call("POST", "/users", GOOD)
    assert status == 201
    assert call("POST", "/sessions", {"email": "student@example.org", "password": "correct horse"}) == (200, body)
    with database.transaction() as tx:
        stored = repo.user_by_email(tx, "student@example.org")
    assert stored["id"] == body["user_id"] and "correct horse" not in stored["hash"]


@pytest.mark.parametrize("body", [{}, {"email": "a@b.org"}, {"email": "nobody", "password": "long enough"},
                                  {"email": "a@b.org", "password": "short"},
                                  {"email": "a@b.org", "password": "x" * 129},
                                  {"email": 5, "password": "long enough"},
                                  {"email": "a" * 250 + "@b.org", "password": "long enough"}])
def test_register_rejects_bad_input(database, body):
    assert call("POST", "/users", body)[0] == 400


def test_an_email_registers_once(database):
    call("POST", "/users", GOOD)
    assert call("POST", "/users", GOOD)[0] == 409


@pytest.mark.parametrize("body", [{"email": "student@example.org", "password": "wrong password"},
                                  {"email": "nobody@example.org", "password": "correct horse"}, {}])
def test_wrong_credentials_are_refused_without_saying_which_part(database, body):
    call("POST", "/users", GOOD)
    assert call("POST", "/sessions", body) == (401, {"error": "wrong email or password"})


def test_profile_is_saved_read_and_validated(database):
    user_id = call("POST", "/users", GOOD)[1]["user_id"]
    path = f"/users/{user_id}/profile"
    assert call("GET", path)[0] == 404
    profile = PROFILE | {"user_id": user_id}
    assert call("PUT", path, profile) == (200, profile | {"version": 1})
    assert call("GET", path) == (200, profile | {"version": 1})
    assert call("PUT", path, profile | {"goal": "fun"})[0] == 400
    assert call("PUT", "/users/u_other/profile", profile)[0] == 400


def test_without_a_database_the_routes_say_unavailable(monkeypatch):
    monkeypatch.setattr(app, "database", None)
    assert call("POST", "/users", GOOD) == (503, {"error": "the database is not configured"})
