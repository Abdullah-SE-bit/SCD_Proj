"""M2 rules: validation, ownership and units of work. Routes call this; only this calls the repositories."""

from typing import Any

from scd_profile import repositories as repo
from scd_profile.db import Database

MAX_TITLE, MAX_TEXT, MAX_ITEMS = 200, 2000, 50
COMPUTE = ("laptop", "free_gpu", "paid")
GOALS = ("startup", "portfolio", "course_project")
# contract field (student-profile.schema.json) -> column name (entities.md)
COLUMNS = {"user_id": "user_id", "skills": "skills", "hours_per_week": "hours", "team_size": "team", "goal": "goal",
           "weeks_available": "weeks_available", "compute": "compute", "interests": "interests"}


class Invalid(ValueError):
    """The request is wrong; the message says which field."""


class NotFound(LookupError):
    """No such record for this user."""


def _text(value: Any, limit: int) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def check_profile(profile: dict[str, Any]) -> None:
    """The rules of contracts/schemas/student-profile.schema.json, with size limits."""
    wrong = sorted(set(profile) ^ set(COLUMNS))
    if wrong:
        raise Invalid(f"missing or unknown fields: {', '.join(wrong)}")
    hours, weeks, team = profile["hours_per_week"], profile["weeks_available"], profile["team_size"]
    checks = {
        "user_id": _text(profile["user_id"], MAX_TITLE),
        "hours_per_week": type(hours) in (int, float) and 0 <= hours <= 168,
        "weeks_available": type(weeks) is int and 0 <= weeks <= 520,
        "team_size": type(team) is int and 1 <= team <= 100,
        "compute": profile["compute"] in COMPUTE,
        "goal": profile["goal"] in GOALS,
    }
    for name in ("skills", "interests"):
        items = profile[name]
        checks[name] = (isinstance(items, list) and len(items) <= MAX_ITEMS
                        and all(_text(item, MAX_TITLE) for item in items))
    bad = [name for name, ok in checks.items() if not ok]
    if bad:
        raise Invalid(f"invalid value: {', '.join(bad)}")


class ProfileService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_profile(self, user_id: str, profile: dict[str, Any]) -> dict[str, Any]:
        check_profile(profile)
        if profile["user_id"] != user_id:
            raise Invalid("invalid value: user_id")
        with self.database.transaction() as tx:
            repo.save_profile(tx, {column: profile[field] for field, column in COLUMNS.items()})
        return self.profile(user_id)

    def profile(self, user_id: str) -> dict[str, Any]:
        with self.database.transaction() as tx:
            row = repo.profile_of(tx, user_id)
        if not row:
            raise NotFound("no profile saved")
        return {field: row[column] for field, column in COLUMNS.items()} | {"version": row["version"]}

    def create_idea(self, user_id: str, title: str, text: str, source: str) -> dict[str, Any]:
        if not _text(title, MAX_TITLE) or not _text(text, MAX_TEXT) or source not in ("own", "generated"):
            raise Invalid("an idea needs a title, a text and the source own or generated")
        with self.database.transaction() as tx:
            idea_id = repo.add_idea(tx, user_id, title, source)
            version_id, version = repo.add_version(tx, idea_id, text)
        return {"idea_id": idea_id, "version_id": version_id, "version": version}

    def revise_idea(self, user_id: str, idea_id: str, text: str) -> dict[str, Any]:
        if not _text(text, MAX_TEXT):
            raise Invalid("invalid value: text")
        with self.database.transaction() as tx:
            found = repo.idea(tx, idea_id)
            if not found or found["user_id"] != user_id:
                raise NotFound("no such idea")
            version_id, version = repo.add_version(tx, idea_id, text)
        return {"idea_id": idea_id, "version_id": version_id, "version": version}
