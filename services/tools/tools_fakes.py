"""A fake network for tool-layer tests: no real connection is ever made."""

from scd_tools.transport import Response

PUBLIC = "93.184.216.34"
API = "https://hacker-news.firebaseio.com/v0/item/1.json"


class Network:
    def __init__(self, *replies, address=PUBLIC):
        self.replies = list(replies)
        self.calls = []
        self.address = address

    def resolve(self, host):
        return [self.address]

    def send(self, method, host, address, target, headers, body, timeout, max_bytes):
        self.calls.append({"method": method, "host": host, "address": address, "target": target,
                           "headers": headers, "body": body})
        reply = self.replies.pop(0) if self.replies else ok("{}")
        if isinstance(reply, Exception):
            raise reply
        return reply


def ok(text, content_type="application/json", status=200, **headers):
    return Response(status, {"content-type": content_type, **headers}, text.encode())
