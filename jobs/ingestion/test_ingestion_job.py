"""The ingestion run: items to cards in the store, chunks to the index, a snapshot, and nothing twice.

(M6I-001, M6I-002, DBS-002, ETH-006.) The items are invented; the store runs on SQLite here.
"""

import json
import sqlite3

import pytest
from scd_ingestion import job
from scd_ingestion.store import Store


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


class Index:
    def __init__(self):
        self.chunks, self.fail = {}, False

    def add(self, chunks):
        if self.fail:
            raise RuntimeError("index down")
        self.chunks.update({c["chunk_id"]: c for c in chunks})
        return len(chunks)


@pytest.fixture
def store(tmp_path):
    store = Store(lambda: Connection(tmp_path / "kb.db"))
    store.migrate()
    return store


def write_items(folder, name, items):
    (folder / name).write_text("".join(json.dumps(i) + "\n" for i in items), encoding="utf-8")


def item(n, source="github"):
    return {"source": source, "external_id": str(n), "url": f"https://example.org/{source}/{n}",
            "title": f"{source} tool {n}", "text": f"Tool number {n} from {source}.", "created_at": None,
            "signals": {}, "retrieved_at": "2026-11-28T10:00:00+00:00"}


def test_a_run_stores_cards_indexes_them_and_counts_by_source(store, tmp_path):
    write_items(tmp_path, "github-1.jsonl", [item(1), item(2), item(1)])
    write_items(tmp_path, "hackernews-1.jsonl", [item(3, "hackernews")])
    index = Index()
    report = job.run(tmp_path, store, index)
    assert report["read"] == 4 and report["added"] == 3 and report["dropped"] == 1
    assert report["cards"] == {"github": 2, "hackernews": 1} and report["indexed"] == 3
    assert len(index.chunks) == 3


def test_running_again_adds_nothing(store, tmp_path):
    write_items(tmp_path, "github-1.jsonl", [item(1)])
    job.run(tmp_path, store, Index())
    index = Index()
    report = job.run(tmp_path, store, index)
    assert (report["added"], report["indexed"], report["cards"]) == (0, 0, {"github": 1})
    assert index.chunks == {}
    assert sorted(r["added"] for r in store.runs()) == [0, 1]  # both runs recorded (same-second order is free)


def test_cards_not_yet_indexed_are_indexed_by_the_next_run(store, tmp_path):
    write_items(tmp_path, "github-1.jsonl", [item(1)])
    broken = Index()
    broken.fail = True
    with pytest.raises(RuntimeError):
        job.run(tmp_path, store, broken)
    index = Index()
    assert job.run(tmp_path, store, index)["indexed"] == 1
    assert index.chunks


def test_unreadable_lines_are_counted_not_fatal(store, tmp_path):
    (tmp_path / "github-1.jsonl").write_text("not json\n[1]\n" + json.dumps(item(1)) + "\n", encoding="utf-8")
    report = job.run(tmp_path, store, Index())
    assert (report["read"], report["added"], report["unreadable"]) == (1, 1, 2)


def test_the_snapshot_restores_the_knowledge_base_without_any_source(store, tmp_path):
    write_items(tmp_path, "github-1.jsonl", [item(1), item(2)])
    job.run(tmp_path, store, Index())
    snapshot = tmp_path / "snapshot.jsonl"
    assert job.write_snapshot(store, snapshot) == 2
    empty = Store(lambda: Connection(tmp_path / "restored.db"))
    empty.migrate()
    index = Index()
    assert job.restore(snapshot, empty, index)["added"] == 2
    assert empty.cards() == store.cards() and len(index.chunks) == 2
