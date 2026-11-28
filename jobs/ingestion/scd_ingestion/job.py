"""M6i ingestion: scout files to idea cards, the vector index and a snapshot. Safe to run again.

Reads every *.jsonl in SCOUT_OUT, stores the cards that are new, indexes the stored cards that are not indexed
yet, and writes the whole card set to SNAPSHOT. `--restore FILE` rebuilds the store and index from a snapshot
without any source. Without database settings it says so and exits 0 (the cluster does not pass them yet).
"""

import json
import os
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import quote

from scd_ingestion import embed
from scd_ingestion.cards import new_cards
from scd_ingestion.chunks import chunks_of
from scd_ingestion.index import VectorIndex
from scd_ingestion.store import Store

BATCH = 200  # cards indexed and marked together, so a stopped run resumes where it was


def log(**fields: Any) -> None:
    print(json.dumps({"job": "ingestion", **fields}), flush=True)


def lines_of(path: Path) -> Iterator[dict[str, Any] | None]:
    """Each line as an item, or None when it is not a JSON object."""
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.strip():
                try:
                    value = json.loads(line)
                except ValueError:
                    value = None
                yield value if isinstance(value, dict) else None


def index_pending(store: Store, index: Any) -> int:
    cards = store.cards(only_unindexed=True)
    for start in range(0, len(cards), BATCH):
        part = cards[start:start + BATCH]
        index.add([chunk for card in part for chunk in chunks_of(card)])
        store.mark_indexed([card["id"] for card in part])
        log(event="indexed", cards=start + len(part), of=len(cards))
    return len(cards)


def run(folder: Path, store: Store, index: Any) -> dict[str, Any]:
    found: list[dict[str, Any] | None] = []
    for path in sorted(folder.glob("*.jsonl")):
        found.extend(lines_of(path))
    items = [item for item in found if item is not None]
    added = new_cards(items, store.cards())
    store.add(added)
    for source in sorted({str(item.get("source")) for item in items}):
        read = sum(1 for item in items if str(item.get("source")) == source)
        new = sum(1 for card in added if card["source"] == source)
        store.record_run(source, new, read - new)
    indexed = index_pending(store, index)
    return {"read": len(items), "unreadable": len(found) - len(items), "added": len(added),
            "dropped": len(items) - len(added), "indexed": indexed, "cards": store.counts()}


def write_snapshot(store: Store, path: Path) -> int:
    cards = store.cards()
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".partial")
    partial.write_text("".join(json.dumps(card, sort_keys=True) + "\n" for card in cards), encoding="utf-8")
    partial.replace(path)  # readers only ever see a complete file
    return len(cards)


def restore(snapshot: Path, store: Store, index: Any) -> dict[str, Any]:
    cards = [card for card in lines_of(snapshot) if card is not None]
    known = {card["id"] for card in store.cards()}
    added = [card for card in cards if card["id"] not in known]
    store.add(added)
    return {"read": len(cards), "added": len(added), "indexed": index_pending(store, index), "cards": store.counts()}


def database_url(env: Any) -> str | None:
    if env.get("DATABASE_URL"):
        return env["DATABASE_URL"]
    names = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_DB")
    if not all(env.get(name) for name in names):
        return None
    user, password, host, database = (env[name] for name in names)
    return f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}@{host}:5432/{database}"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    url = database_url(os.environ)
    if not url:
        log(status="not configured", message="no database settings; nothing done")
        return 0
    store = Store.from_url(url)
    store.migrate()
    index = VectorIndex(os.environ.get("VECTOR_STORE_URL", "http://qdrant:6333"), embed.embed, embed.SIZE)
    if args[:1] == ["--restore"] and len(args) == 2:
        log(status="restored", **restore(Path(args[1]), store, index))
        return 0
    report = run(Path(os.environ.get("SCOUT_OUT", "/data/raw")), store, index)
    snapshot = os.environ.get("SNAPSHOT")
    if snapshot:
        report["snapshot_cards"] = write_snapshot(store, Path(snapshot))
    log(status="completed", **report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
