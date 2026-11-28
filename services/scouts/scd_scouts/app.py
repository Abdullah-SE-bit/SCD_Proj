"""M4 scouts: on-demand scouting over HTTP; the CronJob runs scd_scouts.run (M04-002)."""

from typing import Any

from scd_scouts import run
from scd_scouts.base import Request, Service
from scd_scouts.client import Tools

MAX_LIMIT = 100
service = Service("scouts", "M4")
tool_layer = Tools()


@service.route("POST", "/scout")
def scout(request: Request) -> tuple[int, Any]:
    body = request["body"]
    source, limit, query = body.get("source"), body.get("limit", 20), body.get("query")
    if source not in run.SOURCES:
        return 400, {"error": f"source must be one of {', '.join(run.SOURCES)}"}
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        return 400, {"error": f"limit must be 1 to {MAX_LIMIT}"}
    if query is not None and (not isinstance(query, str) or not 1 <= len(query) <= 100):
        return 400, {"error": "query must be 1 to 100 characters"}
    items, error = run.collect(source, tool_layer, limit, query)
    status = 502 if error and not items else 200
    return status, {"source": source, "items": items, "error": error}


if __name__ == "__main__":
    service.run()
