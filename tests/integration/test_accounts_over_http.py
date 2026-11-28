"""Gateway to profile over real HTTP: register, log in, save and read a profile (USR-001, API-003)."""

import importlib
import json
import sqlite3
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "services" / "gateway"), str(ROOT / "services" / "profile")]

gateway = importlib.import_module("scd_gateway.app")
upstream = importlib.import_module("scd_gateway.upstream")
limits = importlib.import_module("scd_gateway.limits")
profile_app = importlib.import_module("scd_profile.app")
db = importlib.import_module("scd_profile.db")
migrate = importlib.import_module("scd_profile.migrate")


class Cursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, sql, args=()):
        self.cursor.execute(sql.replace("%s", "?"), tuple(args))

    def __getattr__(self, name):
        return getattr(self.cursor, name)


class Connection:
    def __init__(self, path):
        self.raw = sqlite3.connect(path)

    def cursor(self):
        return Cursor(self.raw.cursor())

    def __getattr__(self, name):
        return getattr(self.raw, name)


def test_account_journey(tmp_path, monkeypatch):
    database = db.Database(lambda: Connection(tmp_path / "m2.db"))
    migrate.migrate(database)
    monkeypatch.setattr(profile_app, "database", database)
    server = profile_app.service.server(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(gateway, "profile", upstream.Client(f"http://127.0.0.1:{server.server_address[1]}"))
    monkeypatch.setattr(gateway, "limiter", limits.RateLimiter())

    def call(method, path, body=None, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        return gateway.service.handle(method, path, json.dumps(body).encode() if body else b"", headers)

    try:
        credentials = {"email": "student@example.org", "password": "correct horse"}
        assert call("POST", "/auth/register", credentials)[0] == 201
        assert call("POST", "/auth/register", credentials)[0] == 409
        token = call("POST", "/auth/login", credentials)[1]["token"]
        assert call("GET", "/profile", token=token)[0] == 404
        example = json.loads((ROOT / "contracts/schemas/examples/student-profile.valid.json").read_text("utf-8"))
        del example["user_id"]
        status, saved = call("PUT", "/profile", example, token)
        assert status == 200 and saved["version"] == 1
        assert call("PUT", "/profile", example | {"hours_per_week": 3}, token)[1]["version"] == 2
        assert call("GET", "/profile", token=token)[1]["hours_per_week"] == 3
    finally:
        server.shutdown()
        server.server_close()
