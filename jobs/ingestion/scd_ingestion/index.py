"""Write chunks to the Qdrant vector store over its REST API. The embedding function is passed in.

A point's id comes from the chunk id, so indexing the same chunk again replaces it.
"""

import json
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable, Sequence
from typing import Any

Embed = Callable[[list[str]], list[list[float]]]
Send = Callable[..., tuple[int, Any]]


class IndexFailed(RuntimeError):
    """The vector store refused, or the vectors do not fit the collection."""


def http(method: str, url: str, body: Any = None) -> tuple[int, Any]:
    if not url.startswith(("http://", "https://")):
        raise IndexFailed("the vector store address starts with http:// or https://")
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # nosec B310
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, None


class VectorIndex:
    def __init__(self, base: str, embed: Embed, size: int, send: Send = http, collection: str = "chunks",
                 batch: int = 64) -> None:
        self.url = f"{base.rstrip('/')}/collections/{collection}"
        self.embed, self.size, self.send, self.batch = embed, size, send, batch

    def _expect(self, method: str, url: str, body: Any = None) -> None:
        status, _ = self.send(method, url, body)
        if status != 200:
            raise IndexFailed(f"{method} {url} answered {status}")

    def ensure(self) -> None:
        status, _ = self.send("GET", self.url)
        if status == 404:
            self._expect("PUT", self.url, {"vectors": {"size": self.size, "distance": "Cosine"}})
        elif status != 200:
            raise IndexFailed(f"GET {self.url} answered {status}")

    def add(self, chunks: Sequence[dict[str, Any]]) -> int:
        self.ensure()
        for start in range(0, len(chunks), self.batch):
            part = chunks[start:start + self.batch]
            vectors = self.embed([chunk["text"] for chunk in part])
            if len(vectors) != len(part) or any(len(vector) != self.size for vector in vectors):
                raise IndexFailed(f"the model returned vectors of another size than {self.size}")
            points = [{"id": str(uuid.uuid5(uuid.NAMESPACE_URL, chunk["chunk_id"])), "vector": vector,
                       "payload": chunk} for chunk, vector in zip(part, vectors, strict=True)]
            self._expect("PUT", f"{self.url}/points?wait=true", {"points": points})
        return len(chunks)
