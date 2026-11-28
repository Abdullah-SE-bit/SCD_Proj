"""Turn scout items into idea cards, once each. Only what the source said: unknown fields stay empty.

Item text is untrusted data. Markup is removed here; nothing in it is ever executed or followed.
"""

import hashlib
import html
import re
from collections.abc import Iterable
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

Card = dict[str, Any]
TRACKING = re.compile(r"^(utm_.*|ref|ref_src|fbclid|gclid|mc_cid|mc_eid)$", re.I)
MAX_SUMMARY, MAX_TEXT, MAX_TAGS = 200, 4000, 8


def plain(text: Any) -> str:
    """Tags dropped, entities decoded, whitespace collapsed."""
    if not isinstance(text, str):
        return ""
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", text)).split())


def canonical_url(url: str) -> str:
    """One spelling per page: https, lower-case host without www, no fragment, tracking or trailing slash."""
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").removeprefix("www.")
    if parts.port and parts.port not in (80, 443):
        host = f"{host}:{parts.port}"
    query = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not TRACKING.match(k))
    return urlunsplit(("https", host, parts.path.rstrip("/"), urlencode(query), ""))


def content_key(card: Card) -> str:
    return hashlib.sha256(re.sub(r"\W+", " ", card["text"].lower()).strip().encode()).hexdigest()


def card_from(item: dict[str, Any]) -> Card | None:
    """None when the item lacks a source, an http address, a title or a retrieval time."""
    url, source, fetched = item.get("url"), item.get("source"), item.get("retrieved_at")
    name = re.sub(r"^(show|ask|launch|tell) hn:\s*", "", plain(item.get("title")), flags=re.I)
    if not (name and source and isinstance(fetched, str) and isinstance(url, str)
            and urlsplit(url).scheme in ("http", "https") and urlsplit(url).hostname):
        return None
    address = canonical_url(url)
    body = plain(item.get("text"))
    first = re.split(r"(?<=[.!?])\s", body, maxsplit=1)[0] if body else name
    topics = (item.get("signals") or {}).get("topics")
    tags = [re.sub(r"\W+", "-", plain(t).lower()).strip("-") for t in topics or [] if isinstance(t, str)]
    created = item.get("created_at")
    return {
        "id": "card_" + hashlib.sha256(address.encode()).hexdigest()[:16],
        "name": name, "summary": first[:MAX_SUMMARY], "problem": "", "customer": "",
        "niche_tags": [t for t in dict.fromkeys(tags) if t][:MAX_TAGS], "stage": "unknown", "funding_usd": None,
        "source": source, "url": address,
        "published_at": created[:10] if isinstance(created, str) else None, "fetched_at": fetched,
        "text": (f"{name}. {body}" if body else name)[:MAX_TEXT],
    }


def new_cards(items: Iterable[dict[str, Any]], known: Iterable[Card]) -> list[Card]:
    """Cards for the items that are not already known, by address or by content, in the order given."""
    addresses, contents = set(), set()
    for old in known:
        addresses.add(old["url"])
        contents.add(content_key(old))
    added = []
    for item in items:
        card = card_from(item)
        if card is None:
            continue
        key = content_key(card)
        if card["url"] not in addresses and key not in contents:
            addresses.add(card["url"])
            contents.add(key)
            added.append(card)
    return added
