"""The shared service base drops the query string; the gateway needs it for GET /compare.

The query is handed to the route as the header x-query. A client's own header of that name is discarded.
"""

from typing import Any
from urllib.parse import parse_qs

from scd_gateway.base import Request, Service

HEADER = "x-query"


class QueryService(Service):
    def handle(self, method: str, path: str, raw: bytes = b"",
               headers: dict[str, str] | None = None) -> tuple[int, Any]:
        path, _, query = path.partition("?")
        kept = {name: value for name, value in (headers or {}).items() if name.lower() != HEADER}
        return super().handle(method, path, raw, {**kept, HEADER: query})


def parameters(request: Request) -> dict[str, list[str]]:
    return parse_qs(request["headers"].get(HEADER, ""), max_num_fields=20)
