"""Knowledge records in PostgreSQL: cards, where they came from, and ingestion runs (DBS-002).

ponytail: niches and niche_stats are filled by M7 (P07.01), which adds their tables.
"""

import importlib
import json
import uuid
from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager
from typing import Any
from urllib.parse import unquote, urlsplit

Card = dict[str, Any]
TABLES = (
    "CREATE TABLE IF NOT EXISTS cards (id TEXT PRIMARY KEY, name TEXT NOT NULL, source TEXT NOT NULL, "
    "url TEXT NOT NULL UNIQUE, document TEXT NOT NULL, indexed INTEGER NOT NULL DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS card_sources (card_id TEXT NOT NULL REFERENCES cards (id), platform TEXT NOT NULL, "
    "url TEXT NOT NULL UNIQUE, fetched_at TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS ingestion_runs (run_id TEXT PRIMARY KEY, source TEXT NOT NULL, "
    "added INTEGER NOT NULL, dropped INTEGER NOT NULL, finished_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)",
)


class Store:
    def __init__(self, connect: Callable[[], Any]) -> None:
        self.connect = connect

    @classmethod
    def from_url(cls, url: str) -> "Store":
        parts = urlsplit(url)
        settings = {"user": unquote(parts.username or ""), "password": unquote(parts.password or ""),
                    "host": parts.hostname, "port": parts.port or 5432, "database": parts.path.lstrip("/")}
        return cls(lambda: importlib.import_module("pg8000.dbapi").connect(**settings))

    @contextmanager
    def transaction(self) -> Generator[Any]:
        connection = self.connect()
        try:
            yield connection.cursor()
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def migrate(self) -> None:
        with self.transaction() as cursor:
            for statement in TABLES:
                cursor.execute(statement)

    def _select(self, sql: str, args: Sequence[Any] = ()) -> list[Any]:
        with self.transaction() as cursor:
            cursor.execute(sql, args)
            return list(cursor.fetchall())

    def cards(self, only_unindexed: bool = False) -> list[Card]:
        where = " WHERE indexed = 0" if only_unindexed else ""
        return [json.loads(row[0]) for row in self._select(f"SELECT document FROM cards{where} ORDER BY id")]  # nosec B608

    def counts(self) -> dict[str, int]:
        return {row[0]: row[1] for row in self._select("SELECT source, COUNT(*) FROM cards GROUP BY source "
                                                        "ORDER BY source")}

    def add(self, cards: Sequence[Card]) -> None:
        """Store the cards in one transaction; a card already stored is left as it is."""
        with self.transaction() as cursor:
            for card in cards:
                cursor.execute("INSERT INTO cards (id, name, source, url, document) VALUES (%s, %s, %s, %s, %s) "
                               "ON CONFLICT (id) DO NOTHING",
                               (card["id"], card["name"], card["source"], card["url"], json.dumps(card)))
                cursor.execute("INSERT INTO card_sources (card_id, platform, url, fetched_at) "
                               "VALUES (%s, %s, %s, %s) ON CONFLICT (url) DO NOTHING",
                               (card["id"], card["source"], card["url"], card["fetched_at"]))

    def mark_indexed(self, ids: Sequence[str]) -> None:
        with self.transaction() as cursor:
            for card_id in ids:
                cursor.execute("UPDATE cards SET indexed = 1 WHERE id = %s", (card_id,))

    def record_run(self, source: str, added: int, dropped: int) -> None:
        with self.transaction() as cursor:
            cursor.execute("INSERT INTO ingestion_runs (run_id, source, added, dropped) VALUES (%s, %s, %s, %s)",
                           (f"ingest_{uuid.uuid4().hex}", source, added, dropped))

    def runs(self) -> list[dict[str, Any]]:
        rows = self._select("SELECT source, added, dropped FROM ingestion_runs ORDER BY finished_at, run_id")
        return [{"source": row[0], "added": row[1], "dropped": row[2]} for row in rows]
