"""M6 knowledge base: POST /search returns ranked evidence items; GET /coverage reports what is held.

Without database settings the probes work and both routes answer 503.
"""

import datetime
import os
from functools import partial
from typing import Any
from urllib.parse import quote

from scd_kb import models, search
from scd_kb.base import Request, Service, log
from scd_kb.corpus import Corpus, Unavailable, fetched_times

MAX_QUERY = 500
FILTERS = ("date_from", "date_to", "source", "niche")


def database_url(env: Any) -> str | None:
    if env.get("DATABASE_URL"):
        return env["DATABASE_URL"]
    names = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_DB")
    if not all(env.get(name) for name in names):
        return None
    user, password, host, database = (env[name] for name in names)
    return f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}@{host}:5432/{database}"


url = database_url(os.environ)
engine: search.Search | None = None
if url:
    corpus = Corpus(os.environ.get("VECTOR_STORE_URL", "http://qdrant:6333"), partial(fetched_times, url))
    engine = search.Search(corpus, models.embed, models.rerank)

service = Service("kb", "M6")


def problem(body: dict[str, Any]) -> str | None:
    """What is wrong with a search request (contracts/openapi/kb.json), or None."""
    query, filters = body.get("query"), body.get("filters", {})
    if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY:
        return f"query must be text of 1 to {MAX_QUERY} characters"
    if not isinstance(filters, dict) or set(filters) - set(FILTERS):
        return f"filters may hold only {', '.join(FILTERS)}"
    for name, value in filters.items():
        if not isinstance(value, str) or not value or len(value) > 100:
            return f"invalid filter: {name}"
        if name.startswith("date_"):
            try:
                if datetime.date.fromisoformat(value).isoformat() != value:
                    return f"{name} must be YYYY-MM-DD"
            except ValueError:
                return f"{name} must be YYYY-MM-DD"
    return None


@service.route("POST", "/search")
def post_search(request: Request) -> tuple[int, Any]:
    wrong = problem(request["body"])
    if wrong:
        return 400, {"error": wrong}
    if engine is None:
        return 503, {"error": "the knowledge base is not configured"}
    try:
        return 200, engine.query(request["body"]["query"], request["body"].get("filters"))
    except Unavailable as error:
        log(service="kb", error=str(error))
        return 503, {"error": "the knowledge base is unavailable"}


@service.route("GET", "/coverage")
def get_coverage(_: Request) -> tuple[int, Any]:
    if engine is None:
        return 503, {"error": "the knowledge base is not configured"}
    try:
        return 200, search.coverage(engine.corpus.chunks())
    except Unavailable as error:
        log(service="kb", error=str(error))
        return 503, {"error": "the knowledge base is unavailable"}


if __name__ == "__main__":
    service.run()
