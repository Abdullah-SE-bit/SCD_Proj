"""Forward-only migrations: `python -m scd_profile.migrate` brings an empty or older database to head.

Each file in migrations/ runs once, in name order, inside one transaction. Never edit an applied file.
Statements are separated by a semicolon at the end of a line.
"""

import os
import re
import sys
from pathlib import Path

from scd_profile.db import Database, url_from_env

FOLDER = Path(__file__).with_name("migrations")


def pending(database: Database, folder: Path = FOLDER) -> list[str]:
    with database.transaction() as tx:
        tx.run("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, "
               "applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        done = {row["name"] for row in tx.all("SELECT name FROM schema_migrations")}
    return [path.name for path in sorted(folder.glob("*.sql")) if path.name not in done]


def migrate(database: Database, folder: Path = FOLDER) -> list[str]:
    """Apply what is pending and return the names applied."""
    names = pending(database, folder)
    for name in names:
        text = re.sub(r"^\s*--.*$", "", (folder / name).read_text(encoding="utf-8"), flags=re.M)
        with database.transaction() as tx:
            # SQLite (tests) only opens a transaction on a data change, so record the name first.
            tx.run("INSERT INTO schema_migrations (name) VALUES (%s)", (name,))
            for statement in re.split(r";\s*$", text, flags=re.M):
                if statement.strip():
                    tx.run(statement)
    return names


def main() -> int:
    url = url_from_env(os.environ)
    if not url:
        print("set DATABASE_URL, or POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST and POSTGRES_DB", file=sys.stderr)
        return 1
    applied = migrate(Database.from_url(url))
    print("applied: " + ", ".join(applied) if applied else "database already at head")
    return 0


if __name__ == "__main__":
    sys.exit(main())
