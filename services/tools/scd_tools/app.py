"""M5 tool layer: the single controlled way out to the internet (M05-001, ARC-007)."""

from typing import Any

from scd_tools import fetch, limits, llm, policy
from scd_tools.base import Request, Service

service = Service("tools", "M5")
fetcher = fetch.Fetcher()
proxy = llm.Proxy()


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


@service.route("POST", "/llm")
def post_llm(request: Request) -> tuple[int, Any]:
    try:
        return 200, proxy.complete(request["body"], request["run_id"])
    except llm.Invalid as error:
        return 400, {"error": str(error)}
    except llm.OverBudget as error:
        return 429, {"error": str(error), "budget_exceeded": True}
    except llm.Unavailable as error:
        return 503, {"error": str(error)}
    except llm.ProviderError as error:
        return 502, {"error": str(error), "retry_after": error.retry_after}


if __name__ == "__main__":
    service.run()
