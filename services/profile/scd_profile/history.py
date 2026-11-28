"""Idea history (USR-009): a user's ideas, their versions and the verdict of each. Only the owner can read them."""

from typing import Any

from scd_profile import repositories as repo
from scd_profile.db import Transaction
from scd_profile.services import Invalid, NotFound, ProfileService

VERDICTS = ("GO", "PIVOT", "NO-GO", "INSUFFICIENT_EVIDENCE")
DIMENSIONS = ("demand_pain", "competition", "differentiation", "feasibility", "risk", "learning")
SUMMARY = ("verdict", "score", "confidence", "stability", "weakest_dimension")


def owned(tx: Transaction, user_id: str, idea_id: str) -> dict[str, Any]:
    found = repo.idea(tx, idea_id)
    if not found or found["user_id"] != user_id:
        raise NotFound("no such idea")
    return found


def latest_verdict(tx: Transaction, version_id: str) -> dict[str, Any] | None:
    found = repo.verdicts_of(tx, version_id)
    return found[-1] if found else None


def summary(row: dict[str, Any] | None) -> dict[str, Any] | None:
    return {name: row["document"].get(name) for name in SUMMARY} if row else None


def ideas(records: ProfileService, user_id: str) -> dict[str, Any]:
    """Every idea of the user with its newest version and that version's verdict."""
    with records.database.transaction() as tx:
        listed = []
        for row in repo.ideas_of(tx, user_id):
            versions = repo.versions_of(tx, row["id"])
            newest = versions[-1] if versions else None
            listed.append({"idea_id": row["id"], "title": row["title"], "source": row["source"],
                           "versions": len(versions), "latest_version": newest["version"] if newest else None,
                           "verdict": summary(latest_verdict(tx, newest["id"])) if newest else None})
    return {"ideas": listed}


def versions(records: ProfileService, user_id: str, idea_id: str) -> dict[str, Any]:
    with records.database.transaction() as tx:
        found = owned(tx, user_id, idea_id)
        listed = [{"version": row["version"], "version_id": row["id"], "text": row["text"],
                   "created_at": str(row["created_at"]), "verdict": summary(latest_verdict(tx, row["id"]))}
                  for row in repo.versions_of(tx, idea_id)]
    return {"idea_id": idea_id, "title": found["title"], "versions": listed}


def check_verdict(document: dict[str, Any]) -> None:
    """The parts of verdict.schema.json that are stored in columns or shown in history."""
    def within(value: Any, high: float) -> bool:
        return type(value) in (int, float) and 0 <= value <= high

    scores = document.get("scores")
    fine = (document.get("verdict") in VERDICTS and within(document.get("score"), 100)
            and within(document.get("confidence"), 1) and isinstance(scores, list) and len(scores) <= 6
            and all(isinstance(s, dict) and s.get("dimension") in DIMENSIONS and within(s.get("score"), 5)
                    and within(s.get("confidence"), 1) and isinstance(s.get("evidence_ids"), list) for s in scores)
            and len({s["dimension"] for s in scores}) == len(scores))
    if not fine:
        raise Invalid("not a verdict document")


def save_verdict(records: ProfileService, user_id: str, idea_id: str, version: str,
                 document: dict[str, Any]) -> dict[str, Any]:
    """Store M11's answer for one version of the user's idea."""
    check_verdict(document)
    with records.database.transaction() as tx:
        owned(tx, user_id, idea_id)
        row = next((r for r in repo.versions_of(tx, idea_id) if str(r["version"]) == version), None)
        if not row:
            raise NotFound("no such version")
        verdict_id = repo.save_verdict(tx, row["id"], document)
    return {"verdict_id": verdict_id, "version_id": row["id"]}
