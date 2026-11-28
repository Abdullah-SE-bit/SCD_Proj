"""Scout the sources, on demand or from the CronJob (M04-002). One failing source never stops the others (M04-003).

usage: python -m scd_scouts.run [--source NAME ...] [--limit N] [--out DIR]
Writes one JSON-lines file per source into DIR; the ingestion job reads them. Exit 1 only if every source failed.
"""

import argparse
import datetime
import json
import os
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from scd_scouts import github, hackernews, producthunt
from scd_scouts.base import log
from scd_scouts.client import SourceError, Tools

Connector = Callable[[Tools, int, str | None], Iterator[dict[str, Any]]]
SOURCES: dict[str, Connector] = {"hackernews": hackernews.fetch, "github": github.fetch,
                                 "producthunt": producthunt.fetch}


def collect(source: str, tools: Tools, limit: int, query: str | None = None) -> tuple[list[dict[str, Any]], str | None]:
    """(items, error). Items gathered before a failure are kept."""
    items: list[dict[str, Any]] = []
    try:
        for found in SOURCES[source](tools, limit, query):
            items.append(found)
    except SourceError as error:
        return items, str(error)
    except Exception as error:  # a connector bug in one source must not stop the others
        return items, f"{type(error).__name__} in the connector"
    return items, None


def write(directory: Path, source: str, items: list[dict[str, Any]], stamp: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{source}-{stamp}.jsonl"
    partial = target.with_suffix(".partial")
    partial.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8")
    partial.replace(target)  # readers only ever see complete files
    return target


def main(argv: list[str] | None = None, tools: Tools | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", choices=sorted(SOURCES))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("SCOUT_LIMIT", "200")))
    parser.add_argument("--out", default=os.environ.get("SCOUT_OUT", "raw-items"))
    options = parser.parse_args(argv)
    tools = tools or Tools()
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    succeeded = 0
    for source in options.source or list(SOURCES):
        items, error = collect(source, tools, options.limit)
        if items:
            write(Path(options.out), source, items, stamp)
        succeeded += error is None
        log(job="scouts", source=source, items=len(items), error=error)
    return 0 if succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
