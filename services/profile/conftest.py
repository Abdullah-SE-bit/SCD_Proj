"""Database for the M2 tests: SQLite by default (what CI has), PostgreSQL when TEST_DATABASE_URL is set.

The PostgreSQL run drops and recreates the public schema, so point it at a throw-away database only.
"""

import os
import sqlite3

import pytest
from scd_profile.db import Database


class SqliteCursor:
    """The repositories write %s placeholders (PostgreSQL drivers); SQLite wants ?."""

    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, sql, args=()):
        self.cursor.execute(sql.replace("%s", "?"), tuple(args))

    def __getattr__(self, name):
        return getattr(self.cursor, name)


class SqliteConnection:
    def __init__(self, path):
        self.raw = sqlite3.connect(path)
        self.raw.execute("PRAGMA foreign_keys = ON")

    def cursor(self):
        return SqliteCursor(self.raw.cursor())

    def __getattr__(self, name):
        return getattr(self.raw, name)


@pytest.fixture
def empty_database(tmp_path):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        return Database(lambda: SqliteConnection(tmp_path / "m2.db"))
    database = Database.from_url(url)
    with database.transaction() as tx:
        tx.run("DROP SCHEMA public CASCADE")
        tx.run("CREATE SCHEMA public")
    return database
