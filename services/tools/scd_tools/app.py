"""M5 tool layer: the single controlled way out to the internet (M05-001, ARC-007)."""

from typing import Any

from scd_tools import fetch, limits, policy
from scd_tools.base import Request, Service

service = Service("tools", "M5")
fetcher = fetch.Fetcher()


@service.route("POST", "/fetch")
def post_fetch(request: Request) -> tuple[int, Any]:
    body = request["body"]
    try:
        return 200, fetcher.fetch(body.get("url"), body.get("method", "GET"), body.get("payload"))
    except policy.Refused as error:
        return 403, {"error": str(error)}
    except limits.RateLimited as error:
        return 429, {"error": str(error), "retry_after": error.retry_after}
    except fetch.Upstream as error:
        return 502, {"error": str(error)}


if __name__ == "__main__":
    service.run()
