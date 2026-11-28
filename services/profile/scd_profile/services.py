"""M2 rules: validation, ownership and units of work. Routes call this; only this calls the repositories."""

import re
from typing import Any

from scd_profile import passwords
from scd_profile import repositories as repo
from scd_profile.db import Database

MAX_TITLE, MAX_TEXT, MAX_ITEMS = 200, 2000, 50
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
MIN_PASSWORD, MAX_PASSWORD, MAX_EMAIL = 8, 128, 254
NO_USER = passwords.hashed("no such user")  # hashed for unknown emails so both answers take as long
COMPUTE = ("laptop", "free_gpu", "paid")
GOALS = ("startup", "portfolio", "course_project")
# contract field (student-profile.schema.json) -> column name (entities.md)
COLUMNS = {"user_id": "user_id", "skills": "skills", "hours_per_week": "hours", "team_size": "team", "goal": "goal",
           "weeks_available": "weeks_available", "compute": "compute", "interests": "interests"}


class Invalid(ValueError):
    """The request is wrong; the message says which field."""


class NotFound(LookupError):
    """No such record for this user."""


class Exists(ValueError):
    """The record is already there."""


class BadCredentials(PermissionError):
    """Wrong email or password; never says which."""


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

    def register(self, email: Any, password: Any) -> str:
        address = email.strip().lower() if isinstance(email, str) else ""
        if len(address) > MAX_EMAIL or not EMAIL.fullmatch(address):
            raise Invalid("invalid value: email")
        if not isinstance(password, str) or not MIN_PASSWORD <= len(password) <= MAX_PASSWORD:
            raise Invalid(f"the password needs {MIN_PASSWORD} to {MAX_PASSWORD} characters")
        digest = passwords.hashed(password)
        with self.database.transaction() as tx:
            if repo.user_by_email(tx, address):
                raise Exists("this email is already registered")
            return repo.add_user(tx, address, digest)  # a concurrent duplicate fails on the unique constraint

    def authenticate(self, email: Any, password: Any) -> str:
        if not isinstance(email, str) or not isinstance(password, str) or len(password) > MAX_PASSWORD:
            raise BadCredentials
        with self.database.transaction() as tx:
            user = repo.user_by_email(tx, email.strip().lower())
        if not passwords.matches(password, user["hash"] if user else NO_USER) or not user:
            raise BadCredentials
        return user["id"]

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
