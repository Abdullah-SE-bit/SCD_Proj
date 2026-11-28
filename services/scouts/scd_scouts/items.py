"""The raw item every connector returns, whatever the source. Public fields only: no author names."""

import datetime
from typing import Any


def now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def item(source: str, external_id: Any, url: Any, title: Any, text: Any, created_at: Any,
         signals: dict[str, Any]) -> dict[str, Any] | None:
    """None when the source's record lacks what a card needs (an id, an http address and a title)."""
    if external_id is None or not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return None
    if not isinstance(title, str) or not title.strip():
        return None
    return {"source": source, "external_id": str(external_id), "url": url, "title": title.strip()[:300],
            "text": (text if isinstance(text, str) else "").strip()[:4000],
            "created_at": created_at if isinstance(created_at, str) else None,
            "signals": {k: v for k, v in signals.items() if isinstance(v, (int, float, str, list))},
            "retrieved_at": now()}
