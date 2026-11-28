"""Split a card's text into chunks that keep the card id and the fields search filters on."""

import re
from typing import Any

MAX_CHARS = 800  # about 200 tokens, inside the embedding model's 512


def _pieces(text: str) -> list[str]:
    """Sentences, cutting any that is longer than a chunk."""
    sentences = re.split(r"(?<=[.!?]) ", text)
    return [s[i:i + MAX_CHARS] for s in sentences for i in range(0, len(s), MAX_CHARS)]


def chunks_of(card: dict[str, Any]) -> list[dict[str, Any]]:
    texts: list[str] = []
    for piece in _pieces(card["text"]):
        # parts of one cut sentence are full-length, so they never join the chunk before them
        if texts and len(texts[-1]) + 1 + len(piece) <= MAX_CHARS:
            texts[-1] += " " + piece
        else:
            texts.append(piece)
    date = (card["published_at"] or card["fetched_at"])[:10]
    return [{"chunk_id": f"{card['id']}#c{n}", "card_id": card["id"], "text": text, "date": date,
             "source": card["source"], "niche": card["niche_tags"], "url": card["url"]}
            for n, text in enumerate(texts)]
