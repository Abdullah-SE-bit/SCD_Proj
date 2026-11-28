"""Two ideas side by side on all six dimensions (USR-009). A dimension without a score stays empty, never zero."""

from typing import Any

from scd_profile import repositories as repo
from scd_profile.history import DIMENSIONS, latest_verdict, owned, summary
from scd_profile.services import Invalid, ProfileService


def compare(records: ProfileService, user_id: str, wanted: Any) -> dict[str, Any]:
    """The newest version of each of the two ideas, with that version's newest verdict."""
    if (not isinstance(wanted, list) or len(wanted) != 2 or not all(isinstance(i, str) for i in wanted)
            or wanted[0] == wanted[1]):
        raise Invalid("name two different ideas")
    columns = []
    with records.database.transaction() as tx:
        for idea_id in wanted:
            found = owned(tx, user_id, idea_id)
            newest = repo.versions_of(tx, idea_id)[-1]
            verdict = latest_verdict(tx, newest["id"])
            scores = {row["dimension"]: row["score"] for row in repo.scores_of(tx, verdict["id"])} if verdict else {}
            columns.append({"idea_id": idea_id, "title": found["title"], "version": newest["version"],
                            "verdict": summary(verdict),
                            "dimensions": {name: scores.get(name) for name in DIMENSIONS}})
    return {"dimensions": list(DIMENSIONS), "ideas": columns}
