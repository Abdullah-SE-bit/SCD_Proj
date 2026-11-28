"""Scheduled and on-demand scouting, and one failing source (M04-002, M04-003)."""

import json

import pytest
from scd_scouts import app, run
from scouts_fakes import Failure, FakeTools

REPOS = {"search/repositories": {"items": [{"id": 1, "full_name": "o/r", "html_url": "https://github.com/o/r"}]}}
STORY = {"showstories": [7], "askstories": [], "beststories": [], "topstories": [],
         "item/7.json": {"id": 7, "type": "story", "title": "Show HN: x", "time": 1_700_000_000}}


def mixed():
    return FakeTools({**STORY, **REPOS, "producthunt": Failure(502, "api.producthunt.com answered 401")})


def test_a_failing_source_does_not_stop_the_others(tmp_path, capsys):
    assert run.main(["--limit", "5", "--out", str(tmp_path)], mixed()) == 0
    written = sorted(p.name.split("-")[0] for p in tmp_path.glob("*.jsonl"))
    assert written == ["github", "hackernews"] and not list(tmp_path.glob("*.partial"))
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    failed = next(line for line in lines if line["source"] == "producthunt")
    assert "401" in failed["error"] and failed["items"] == 0


def test_each_line_of_a_file_is_one_item(tmp_path):
    run.main(["--source", "github", "--limit", "5", "--out", str(tmp_path)], mixed())
    (path,) = tmp_path.glob("*.jsonl")
    item = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert {"source", "external_id", "url", "title", "text", "created_at", "signals", "retrieved_at"} == set(item)


def test_the_job_fails_only_when_every_source_fails(tmp_path):
    assert run.main(["--out", str(tmp_path)], FakeTools({"": Failure()})) == 1
    assert list(tmp_path.glob("*")) == []


def test_items_gathered_before_a_failure_are_kept():
    tools = FakeTools({"&page=1": {"items": [{"id": n, "full_name": f"o/{n}", "html_url": "https://github.com/o/x"}
                                             for n in range(100)]}, "&page=2": Failure()})
    items, error = run.collect("github", tools, 150, "x")
    assert len(items) == 100 and error


def test_a_connector_bug_is_contained(monkeypatch):
    monkeypatch.setitem(run.SOURCES, "github", lambda *a: iter(1 / 0 for _ in [1]))
    items, error = run.collect("github", mixed(), 5)
    assert items == [] and "ZeroDivisionError" in error


def post(body):
    return app.service.handle("POST", "/scout", json.dumps(body).encode(), {})


def test_on_demand(monkeypatch):
    monkeypatch.setattr(app, "tool_layer", mixed())
    status, answer = post({"source": "github", "limit": 5})
    assert status == 200 and answer["items"][0]["source"] == "github" and answer["error"] is None
    assert post({"source": "producthunt"})[0] == 502


@pytest.mark.parametrize("body", [{}, {"source": "reddit"}, {"source": "github", "limit": 0},
                                  {"source": "github", "limit": 1000}, {"source": "github", "query": 5}])
def test_bad_requests(body):
    assert post(body)[0] == 400
