"""Public accounts and profile: invalid, unauthenticated and over-limit requests are rejected (M01-003, API-003)."""

import json

import pytest
from scd_gateway import app, tokens
from scd_gateway.limits import RateLimiter
from scd_gateway.upstream import Unavailable

LOGIN = {"email": "student@example.org", "password": "correct horse"}


class FakeProfile:
    def __init__(self):
        self.calls = []
        self.answers = {"/users": (201, {"user_id": "u_1"}), "/sessions": (200, {"user_id": "u_1"})}

    def __call__(self, method, path, body=None):
        self.calls.append((method, path, body))
        return self.answers.get(path, (200, body or {"user_id": "u_1"}))


@pytest.fixture
def profile(monkeypatch):
    fake = FakeProfile()
    monkeypatch.setattr(app, "profile", fake)
    monkeypatch.setattr(app, "limiter", RateLimiter())
    return fake


def call(method, path, body=None, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return app.service.handle(method, path, json.dumps(body).encode() if body is not None else b"", headers)


def test_register_and_login_pass_through_and_login_returns_a_token(profile):
    assert call("POST", "/auth/register", LOGIN) == (201, {"user_id": "u_1"})
    status, body = call("POST", "/auth/login", LOGIN)
    assert status == 200 and tokens.user_of(body["token"], app.key) == "u_1"
    assert [c[1] for c in profile.calls] == ["/users", "/sessions"]


def test_refused_login_gives_no_token(profile):
    profile.answers["/sessions"] = (401, {"error": "wrong email or password"})
    assert call("POST", "/auth/login", LOGIN) == (401, {"error": "wrong email or password"})


@pytest.mark.parametrize("body", [{}, {"email": "a@b.org"}, {"email": "a@b.org", "password": 5},
                                  {"email": "x" * 300, "password": "long enough"},
                                  {"email": "a@b.org", "password": "x" * 200}, LOGIN | {"admin": True}])
def test_malformed_credentials_never_reach_the_profile_service(profile, body):
    for path in ("/auth/register", "/auth/login"):
        assert call("POST", path, body)[0] == 400
    assert profile.calls == []


@pytest.mark.parametrize("token", [None, "garbage", "a.b.c"])
def test_profile_needs_a_valid_token(profile, token):
    for method in ("GET", "PUT"):
        assert call(method, "/profile", {} if method == "PUT" else None, token)[0] == 401
    assert profile.calls == []


def test_forged_expired_and_unsigned_tokens_are_refused():
    good = tokens.issue("u_1", app.key, now=1000)
    assert tokens.user_of(good, app.key, now=1000) == "u_1"
    assert tokens.user_of(good, app.key, now=1000 + tokens.LIFETIME + 1) is None
    assert tokens.user_of(good, b"another key", now=1000) is None
    head, claims, _ = good.split(".")
    assert tokens.user_of(f"{head}.{claims}.", app.key, now=1000) is None
    other = tokens.issue("u_2", app.key, now=1000).split(".")[1]
    assert tokens.user_of(f"{head}.{other}.{good.split('.')[2]}", app.key, now=1000) is None


def test_a_user_reads_and_writes_only_their_own_profile(profile):
    token = tokens.issue("u_1", app.key)
    assert call("GET", "/profile", token=token)[0] == 200
    assert call("PUT", "/profile", {"goal": "portfolio"}, token)[0] == 200
    assert profile.calls == [("GET", "/users/u_1/profile", None),
                             ("PUT", "/users/u_1/profile", {"goal": "portfolio", "user_id": "u_1"})]
    assert call("PUT", "/profile", {"user_id": "u_2"}, token)[0] == 403
    assert len(profile.calls) == 2


def test_repeated_logins_for_one_account_are_limited(profile):
    profile.answers["/sessions"] = (401, {"error": "wrong email or password"})
    statuses = [call("POST", "/auth/login", LOGIN)[0] for _ in range(app.LOGINS + 1)]
    assert statuses == [401] * app.LOGINS + [429]
    assert call("POST", "/auth/login", LOGIN | {"email": " STUDENT@example.org"})[0] == 429
    assert call("POST", "/auth/login", LOGIN | {"email": "other@example.org"})[0] == 401


def test_registrations_and_validations_have_a_shared_limit(profile):
    statuses = [call("POST", "/auth/register", LOGIN)[0] for _ in range(app.REGISTRATIONS + 1)]
    assert statuses[-1] == 429 and statuses[:-1] == [201] * app.REGISTRATIONS
    statuses = [call("POST", "/validate", {"idea": "x"})[0] for _ in range(app.VALIDATIONS + 1)]
    assert statuses[-1] == 429 and set(statuses[:-1]) == {200}


def test_the_limit_window_passes():
    now = [0.0]
    limiter = RateLimiter(clock=lambda: now[0])
    assert [limiter.wait("k", 2) for _ in range(3)] == [0, 0, 60]
    now[0] = 61.0
    assert limiter.wait("k", 2) == 0


def test_a_missing_profile_service_is_reported(monkeypatch, profile):
    def down(*_):
        raise Unavailable("no route")

    monkeypatch.setattr(app, "profile", down)
    assert call("POST", "/auth/login", LOGIN) == (503, {"error": "accounts are unavailable"})
