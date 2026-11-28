"""Database access for M2: one short transaction per unit of work over any DB-API connection.

The driver (pg8000) is a run-time dependency only, imported when a PostgreSQL address is used.
"""

import importlib
from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any
from urllib.parse import quote, unquote, urlsplit

Row = dict[str, Any]


class Transaction:
    def __init__(self, cursor: Any) -> None:
        self.cursor = cursor

    def run(self, sql: str, args: Sequence[Any] = ()) -> None:
        """Execute one statement. Values go in `args` for the %s placeholders, never into the SQL text."""
        self.cursor.execute(sql, args)

    def all(self, sql: str, args: Sequence[Any] = ()) -> list[Row]:
        self.run(sql, args)
        names = [column[0] for column in self.cursor.description]
        return [dict(zip(names, row, strict=True)) for row in self.cursor.fetchall()]

    def one(self, sql: str, args: Sequence[Any] = ()) -> Row | None:
        rows = self.all(sql, args)
        return rows[0] if rows else None


class Database:
    def __init__(self, connect: Callable[[], Any]) -> None:
        self.connect = connect

    @classmethod
    def from_url(cls, url: str, driver: Any = None) -> "Database":
        parts = urlsplit(url)
        settings = {"user": unquote(parts.username or ""), "password": unquote(parts.password or ""),
                    "host": parts.hostname, "port": parts.port or 5432, "database": parts.path.lstrip("/")}

        def connect() -> Any:
            module = driver or importlib.import_module("pg8000.dbapi")
            return module.connect(**settings)

        return cls(connect)

    @contextmanager
    def transaction(self) -> Generator[Transaction]:
        """Commit when the block succeeds, roll back when it raises.

        ponytail: a new connection per transaction; add a pool if measured latency asks for it.
        """
        connection = self.connect()
        try:
            yield Transaction(connection.cursor())
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()


def url_from_env(env: Mapping[str, str]) -> str | None:
    """DATABASE_URL, or the POSTGRES_* values the cluster and compose files provide. None when unset."""
    if env.get("DATABASE_URL"):
        return env["DATABASE_URL"]
    names = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_DB")
    if not all(env.get(name) for name in names):
        return None
    user, password, host, database = (env[name] for name in names)
    return f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}@{host}:5432/{database}"
