"""The versioned verdict cache against a small Redis-protocol server (M02-003, M02-004, CMN-002, DBS-003)."""

import socketserver
import threading

import pytest
from scd_profile import app, cache
from test_profile_history import VERDICT, call, database, idea, user  # noqa: F401  (pytest fixture)

VERSIONS = {"rubrics": "r1", "engine": "m11@v2", "snapshot": "s1"}


class FakeRedis(socketserver.ThreadingTCPServer):
    daemon_threads = True

    def __init__(self):
        self.data, self.commands = {}, []
        super().__init__(("127.0.0.1", 0), Handler)


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        count = int(self.rfile.readline()[1:])
        words = []
        for _ in range(count):
            size = int(self.rfile.readline()[1:])
            words.append(self.rfile.read(size + 2)[:size].decode())
        self.server.commands.append(words)
        if words[0] == "SET":
            self.server.data[words[1]] = words[2]
            self.wfile.write(b"+OK\r\n")
        else:
            value = self.server.data.get(words[1])
            raw = None if value is None else value.encode()
            self.wfile.write(b"$-1\r\n" if raw is None else b"$%d\r\n%s\r\n" % (len(raw), raw))


@pytest.fixture
def redis(monkeypatch):
    server = FakeRedis()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    store = cache.Redis(f"redis://127.0.0.1:{server.server_address[1]}/0")
    monkeypatch.setattr(app, "verdicts", cache.VerdictCache(store))
    yield server
    server.shutdown()
    server.server_close()


def saved(owner):
    return f"/users/{owner}/ideas/{idea(owner)}/versions/1/cache"


def test_a_stored_verdict_is_a_hit_and_the_hit_is_visible(database, redis, capsys):  # noqa: F811
    path = saved(user("a@example.org"))
    assert call("POST", f"{path}/lookup", VERSIONS)[1] == {"hit": False, "verdict": None}
    assert call("PUT", path, VERSIONS | {"verdict": VERDICT})[1] == {"stored": True}
    capsys.readouterr()
    assert call("POST", f"{path}/lookup", VERSIONS)[1] == {"hit": True, "verdict": VERDICT}
    assert '"event": "cache_hit"' in capsys.readouterr().out
    metrics = call("GET", "/metrics")[1]
    assert (metrics["cache_hits"], metrics["cache_misses"], metrics["cache"]) == (1, 1, "redis")


def test_every_entry_expires(database, redis):  # noqa: F811
    path = saved(user("a@example.org"))
    call("PUT", path, VERSIONS | {"verdict": VERDICT})
    command = next(words for words in redis.commands if words[0] == "SET")
    assert command[3:] == ["EX", str(cache.TTL_SECONDS)] and command[1].startswith("verdict:")


@pytest.mark.parametrize("changed", ["rubrics", "engine", "snapshot"])
def test_a_new_rubric_engine_or_snapshot_version_misses(database, redis, changed):  # noqa: F811
    path = saved(user("a@example.org"))
    call("PUT", path, VERSIONS | {"verdict": VERDICT})
    assert call("POST", f"{path}/lookup", VERSIONS | {changed: "new"})[1]["hit"] is False


def test_a_changed_profile_misses(database, redis):  # noqa: F811
    owner = user("a@example.org")
    path = saved(owner)
    profile = {"user_id": owner, "skills": [], "hours_per_week": 10, "weeks_available": 8, "team_size": 1,
               "compute": "laptop", "goal": "portfolio", "interests": []}
    assert call("PUT", f"/users/{owner}/profile", profile)[0] == 200
    call("PUT", path, VERSIONS | {"verdict": VERDICT})
    assert call("POST", f"{path}/lookup", VERSIONS)[1]["hit"] is True
    call("PUT", f"/users/{owner}/profile", profile | {"hours_per_week": 20})
    assert call("POST", f"{path}/lookup", VERSIONS)[1]["hit"] is False


def test_each_idea_version_and_user_has_its_own_entry():
    base = dict.fromkeys(cache.KEY_PARTS, "x")
    keys = {cache.key_of(base | {part: "other"}) for part in cache.KEY_PARTS} | {cache.key_of(base)}
    assert len(keys) == len(cache.KEY_PARTS) + 1


def test_without_redis_everything_is_a_miss(database, monkeypatch):  # noqa: F811
    path = saved(user("a@example.org"))
    for store in (None, cache.Redis("redis://127.0.0.1:1", timeout=0.2)):
        monkeypatch.setattr(app, "verdicts", cache.VerdictCache(store))
        assert call("PUT", path, VERSIONS | {"verdict": VERDICT})[1] == {"stored": False}
        assert call("POST", f"{path}/lookup", VERSIONS)[1]["hit"] is False
    assert call("GET", "/metrics")[1]["cache_errors"] == 2


def test_another_user_cannot_read_or_fill_the_cache(database, redis):  # noqa: F811
    owner, other = user("a@example.org"), user("b@example.org")
    path = saved(owner).replace(owner, other)
    assert call("POST", f"{path}/lookup", VERSIONS)[0] == 404
    assert call("PUT", path, VERSIONS | {"verdict": VERDICT})[0] == 404
    assert redis.commands == []


@pytest.mark.parametrize("body", [{}, {"rubrics": "r1"}, VERSIONS | {"engine": 5}])
def test_versions_are_required(database, redis, body):  # noqa: F811
    assert call("POST", f"{saved(user('a@example.org'))}/lookup", body)[0] == 400


@pytest.mark.parametrize("address", ["http://redis:6379", "redis://", "redis"])
def test_a_bad_cache_address_is_refused(address):
    with pytest.raises(ValueError):
        cache.Redis(address)
