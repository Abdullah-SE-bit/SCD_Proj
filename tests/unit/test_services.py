"""Every module answers its probes through the shared base (API-002)."""

import importlib
import json
import sys
import threading
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SERVICES = sorted(p.parents[1].name for p in ROOT.glob("services/*/scd_*/app.py"))
JOBS = sorted(p.parents[1].name for p in ROOT.glob("jobs/*/scd_*/job.py"))


def load(area: str, name: str, part: str):
    sys.path.insert(0, str(ROOT / area / name))
    try:
        return importlib.import_module(f"scd_{name}.{part}")
    finally:
        sys.path.pop(0)


def new_service(**kwargs):
    return load("services", "verdict", "base").Service("probe", "M0", **kwargs)


@pytest.mark.parametrize("name", SERVICES)
def test_service_probes(name):
    service = load("services", name, "app").service
    assert service.handle("GET", "/health") == (200, {"status": "ok", "service": name})
    assert service.handle("GET", "/ready") == (200, {"ready": True, "service": name})
    assert service.handle("GET", "/info")[1]["module"].startswith("M")


@pytest.mark.parametrize("name", JOBS)
def test_job_exits_cleanly(name, capsys):
    assert load("jobs", name, "job").main() == 0
    assert json.loads(capsys.readouterr().out)["job"] == name


def test_base_copies_are_identical():
    copies = {p.read_bytes() for p in ROOT.glob("services/*/scd_*/base.py")}
    assert len(copies) == 1


def test_not_ready_is_503():
    assert new_service(ready=lambda: False).handle("GET", "/ready")[0] == 503


def test_bad_requests_are_rejected():
    service = new_service()
    service.route("POST", "/items/{item}")(lambda request: (200, request["params"]))
    service.route("POST", "/boom")(lambda request: (200, 1 / 0))
    assert service.handle("POST", "/items/a1", b"{}") == (200, {"item": "a1"})
    assert service.handle("POST", "/items/a1", b"not json")[0] == 400
    assert service.handle("POST", "/items/a1", b"[1]")[0] == 400
    assert service.handle("POST", "/items/a1", b"x" * 1_000_001)[0] == 413
    assert service.handle("GET", "/items/a1")[0] == 404
    assert service.handle("POST", "/boom") == (500, {"error": "internal error"})


def test_probes_over_real_http():
    server = new_service().server(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{server.server_address[1]}/health"
        with urllib.request.urlopen(url, timeout=5) as response:
            assert response.status == 200
            assert json.load(response)["status"] == "ok"
    finally:
        server.shutdown()
        server.server_close()
