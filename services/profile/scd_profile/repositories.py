"""SQL for the M2 application records, and nothing else. Every function works inside the caller's transaction."""

import json
import uuid
from typing import Any

from scd_profile.db import Row, Transaction

PROFILE_COLUMNS = "user_id, skills, hours, team, goal, weeks_available, compute, interests, version"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


# users
def add_user(tx: Transaction, email: str, password_hash: str) -> str:
    user_id = new_id("u")
    tx.run("INSERT INTO users (id, email, hash) VALUES (%s, %s, %s)", (user_id, email, password_hash))
    return user_id


def user_by_email(tx: Transaction, email: str) -> Row | None:
    return tx.one("SELECT id, email, hash, created_at FROM users WHERE email = %s", (email,))


# profiles
def save_profile(tx: Transaction, row: Row) -> None:
    """Insert, or replace and raise the version (cache keys include it)."""
    values = [row[name] for name in
              ("user_id", "skills", "hours", "team", "goal", "weeks_available", "compute", "interests")]
    values[1], values[7] = json.dumps(values[1]), json.dumps(values[7])
    tx.run("INSERT INTO profiles (user_id, skills, hours, team, goal, weeks_available, compute, interests) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
           "ON CONFLICT (user_id) DO UPDATE SET skills = excluded.skills, hours = excluded.hours, "
           "team = excluded.team, goal = excluded.goal, weeks_available = excluded.weeks_available, "
           "compute = excluded.compute, interests = excluded.interests, version = profiles.version + 1", values)


def profile_of(tx: Transaction, user_id: str) -> Row | None:
    row = tx.one(f"SELECT {PROFILE_COLUMNS} FROM profiles WHERE user_id = %s", (user_id,))  # nosec B608
    if row:
        row["skills"], row["interests"] = json.loads(row["skills"]), json.loads(row["interests"])
    return row


# ideas and their versions
def add_idea(tx: Transaction, user_id: str, title: str, source: str) -> str:
    idea_id = new_id("idea")
    tx.run("INSERT INTO ideas (id, user_id, title, source) VALUES (%s, %s, %s, %s)", (idea_id, user_id, title, source))
    return idea_id


def idea(tx: Transaction, idea_id: str) -> Row | None:
    return tx.one("SELECT id, user_id, title, source FROM ideas WHERE id = %s", (idea_id,))


def ideas_of(tx: Transaction, user_id: str) -> list[Row]:
    return tx.all("SELECT id, user_id, title, source FROM ideas WHERE user_id = %s ORDER BY title, id", (user_id,))


def add_version(tx: Transaction, idea_id: str, text: str) -> tuple[str, int]:
    latest = tx.one("SELECT COALESCE(MAX(version), 0) AS latest FROM idea_versions WHERE idea_id = %s", (idea_id,))
    version = (latest["latest"] if latest else 0) + 1
    version_id = new_id("ver")
    tx.run("INSERT INTO idea_versions (id, idea_id, version, text) VALUES (%s, %s, %s, %s)",
           (version_id, idea_id, version, text))  # a concurrent duplicate fails on the unique constraint
    return version_id, version


def versions_of(tx: Transaction, idea_id: str) -> list[Row]:
    return tx.all("SELECT id, idea_id, version, text, created_at FROM idea_versions WHERE idea_id = %s "
                  "ORDER BY version", (idea_id,))


# verdicts and dimension scores
def save_verdict(tx: Transaction, version_id: str, document: dict[str, Any]) -> str:
    """Store the verdict as M11 produced it, with its scores in rows for queries and comparison."""
    verdict_id = new_id("verdict")
    tx.run("INSERT INTO verdicts (id, version_id, verdict, score, confidence, document) "
           "VALUES (%s, %s, %s, %s, %s, %s)", (verdict_id, version_id, document["verdict"], document["score"],
                                               document["confidence"], json.dumps(document)))
    for score in document["scores"]:
        tx.run("INSERT INTO dimension_scores (verdict_id, dimension, score, conf, evidence) "
               "VALUES (%s, %s, %s, %s, %s)", (verdict_id, score["dimension"], score["score"], score["confidence"],
                                               json.dumps(score["evidence_ids"])))
    return verdict_id


def verdicts_of(tx: Transaction, version_id: str) -> list[Row]:
    rows = tx.all("SELECT id, version_id, verdict, score, confidence, document FROM verdicts WHERE version_id = %s "
                  "ORDER BY created_at, id", (version_id,))
    return [row | {"document": json.loads(row["document"])} for row in rows]


def scores_of(tx: Transaction, verdict_id: str) -> list[Row]:
    rows = tx.all("SELECT dimension, score, conf, evidence FROM dimension_scores WHERE verdict_id = %s "
                  "ORDER BY dimension", (verdict_id,))
    return [row | {"evidence": json.loads(row["evidence"])} for row in rows]


# approvals, trace index, conversations
def record_approval(tx: Transaction, run_id: str, action: str, decision: str) -> None:
    tx.run("INSERT INTO approvals (run_id, action, decision) VALUES (%s, %s, %s)", (run_id, action, decision))


def approvals_of(tx: Transaction, run_id: str) -> list[Row]:
    return tx.all("SELECT run_id, action, decision FROM approvals WHERE run_id = %s ORDER BY decided_at", (run_id,))


def index_run(tx: Transaction, run_id: str, cost: float, latency: float, status: str) -> None:
    tx.run("INSERT INTO traces_index (run_id, cost, latency, status) VALUES (%s, %s, %s, %s) "
           "ON CONFLICT (run_id) DO UPDATE SET cost = excluded.cost, latency = excluded.latency, "
           "status = excluded.status", (run_id, cost, latency, status))


def run_index(tx: Transaction, run_id: str) -> Row | None:
    return tx.one("SELECT run_id, cost, latency, status FROM traces_index WHERE run_id = %s", (run_id,))


def save_turns(tx: Transaction, idea_id: str, turns: list[dict[str, Any]]) -> None:
    tx.run("INSERT INTO conversations (idea_id, turns) VALUES (%s, %s) "
           "ON CONFLICT (idea_id) DO UPDATE SET turns = excluded.turns", (idea_id, json.dumps(turns)))


def turns_of(tx: Transaction, idea_id: str) -> list[dict[str, Any]]:
    row = tx.one("SELECT turns FROM conversations WHERE idea_id = %s", (idea_id,))
    return json.loads(row["turns"]) if row else []
