"""Which addresses M5 may contact (M05-001, API-007): allow-listed domains over HTTPS on public addresses only."""

import ipaddress
import json
import socket
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import SplitResult, urlsplit

SOURCES = Path(__file__).with_name("sources.json")
Resolver = Callable[[str], list[str]]


class Refused(Exception):
    """The request is not allowed. The message says why and is safe to return to the caller."""


def load_sources(path: Path = SOURCES) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(host: str) -> list[str]:
    return [str(info[4][0]) for info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)]


def check_url(url: Any, sources: dict[str, Any]) -> tuple[SplitResult, dict[str, Any]]:
    """(parts, domain rules) for an allowed URL."""
    if not isinstance(url, str) or not url or len(url) > 2000 or any(ord(c) < 33 or ord(c) > 126 for c in url):
        raise Refused("url must be a printable address without spaces")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        raise Refused("malformed url") from None
    if parts.scheme != "https":
        raise Refused("only https is allowed")
    if parts.username is not None or parts.password is not None:
        raise Refused("credentials in the url are not allowed")
    if port not in (None, 443):
        raise Refused("only the default https port is allowed")
    host = (parts.hostname or "").rstrip(".")
    rules = sources["domains"].get(host)
    if rules is None:
        raise Refused(f"domain is not on the allow-list: {host or 'none'}")
    return parts, rules


def public_address(host: str, resolver: Resolver = resolve) -> str:
    """One resolved address of the host; refused if any address is not public (guards against SSRF)."""
    try:
        addresses = resolver(host)
    except OSError:
        raise ConnectionError(f"cannot resolve {host}") from None
    if not addresses:
        raise ConnectionError(f"cannot resolve {host}")
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%")[0])
        if not ip.is_global or ip.is_multicast:
            raise Refused(f"{host} resolves to a non-public address")
    return next((a for a in addresses if ":" not in a), addresses[0])
