"""The embedding and reranking models, run on the CPU by fastembed. Imported only when used; baked into the image.

The embedding model must be the one the ingestion job indexed with.
"""

import importlib
import os
from functools import cache
from typing import Any

EMBEDDER = "BAAI/bge-small-en-v1.5"
RERANKER = "Xenova/ms-marco-MiniLM-L-6-v2"


def _settings() -> dict[str, Any]:
    return {"cache_dir": os.environ.get("MODEL_DIR", "/app/model"), "threads": 2,
            "local_files_only": os.environ.get("MODEL_DOWNLOAD") != "1"}


@cache
def embedder() -> Any:
    return importlib.import_module("fastembed").TextEmbedding(EMBEDDER, **_settings())


@cache
def reranker() -> Any:
    module = importlib.import_module("fastembed.rerank.cross_encoder")
    return module.TextCrossEncoder(RERANKER, **_settings())


def embed(query: str) -> list[float]:
    return next(iter(embedder().query_embed(query))).tolist()


def rerank(query: str, texts: list[str]) -> list[float]:
    return [float(score) for score in reranker().rerank(query, texts, batch_size=16)]
