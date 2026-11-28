"""The embedding model, bge-small, run on the CPU by fastembed. Imported only when used; baked into the image."""

import importlib
import os
from typing import Any

MODEL = "BAAI/bge-small-en-v1.5"
SIZE = 384
_model: Any = None


def embed(texts: list[str]) -> list[list[float]]:
    global _model
    if _model is None:
        library = importlib.import_module("fastembed")
        _model = library.TextEmbedding(MODEL, cache_dir=os.environ.get("MODEL_DIR", "/app/model"), threads=2,
                                       local_files_only=os.environ.get("MODEL_DOWNLOAD") != "1")
    return [vector.tolist() for vector in _model.embed(texts, batch_size=16)]
