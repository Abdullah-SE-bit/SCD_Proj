"""A fake tool layer for scout tests: answers by address, so no test needs a network."""

import json

from scd_scouts.client import Tools


class FakeTools(Tools):
    """routes: {substring of the address: value, SourceError or list of them used in order}"""

    def __init__(self, routes):
        self.routes = routes
        self.requests = []
        self.pauses = []
        super().__init__("http://tools:8000", self._post, self.pauses.append)

    def _post(self, url, body):
        self.requests.append(body)
        for part, value in self.routes.items():
            if part in body["url"]:
                if isinstance(value, Failure):
                    return value.status, {"error": value.message}
                return 200, {"content": json.dumps(value)}
        return 502, {"error": "not routed"}


class Failure:
    def __init__(self, status=502, message="source failed"):
        self.status, self.message = status, message
