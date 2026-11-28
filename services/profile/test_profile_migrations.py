"""An empty database migrates to head with one command (M2-002, DBS-001)."""

import pytest
from scd_profile.db import Database, url_from_env
from scd_profile.migrate import migrate, pending

# contracts/database/entities.md, application tables with their documented columns
TABLES = {
    "users": "id email hash created_at",
    "profiles": "user_id skills hours team goal weeks_available compute interests version",
    "ideas": "id user_id title source",
    "idea_versions": "id idea_id version text created_at",
    "verdicts": "id version_id verdict score confidence document",
    "dimension_scores": "verdict_id dimension score conf evidence",
    "approvals": "run_id action decision",
    "traces_index": "run_id cost latency status",
    "conversations": "idea_id turns",
}


def test_fresh_database_migrates_to_head(empty_database):
    assert migrate(empty_database) == ["001_application_tables.sql"]
    for table, columns in TABLES.items():
        with empty_database.transaction() as tx:
            tx.run(f"SELECT {', '.join(columns.split())} FROM {table}")  # unknown names fail here


def test_migrating_twice_changes_nothing(empty_database):
    migrate(empty_database)
    assert migrate(empty_database) == []
    assert pending(empty_database) == []


def test_failed_migration_leaves_no_record(empty_database, tmp_path):
    folder = tmp_path / "bad"
    folder.mkdir()
    (folder / "001_bad.sql").write_text("CREATE TABLE half (id TEXT);\nCREATE TABLE half (id TEXT);\n")
    with pytest.raises(Exception, match="half"):
        migrate(empty_database, folder)
    assert pending(empty_database, folder) == ["001_bad.sql"]


def test_database_address_comes_from_the_environment():
    assert url_from_env({"DATABASE_URL": "postgresql://a:b@db:5432/x"}) == "postgresql://a:b@db:5432/x"
    parts = {"POSTGRES_HOST": "postgres", "POSTGRES_USER": "app", "POSTGRES_PASSWORD": "p@ss/word",
             "POSTGRES_DB": "idea_validator"}
    assert url_from_env(parts) == "postgresql://app:p%40ss%2Fword@postgres:5432/idea_validator"
    assert url_from_env({}) is None


def test_url_is_split_for_the_driver():
    calls = {}

    class Driver:
        @staticmethod
        def connect(**kwargs):
            calls.update(kwargs)

    Database.from_url("postgresql://app:p%40ss@postgres:6000/idea", driver=Driver).connect()
    assert calls == {"user": "app", "password": "p@ss", "host": "postgres", "port": 6000, "database": "idea"}
