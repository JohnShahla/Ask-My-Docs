"""Thin wrapper around a persistent Chroma collection.

Embeddings default to Chroma's built-in local model (sentence-transformers via ONNX),
so the index works out of the box with no extra API key. Generation/eval is the only
part that calls Claude.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from .chunking import Chunk


class VectorStore:
    def __init__(
        self,
        persist_dir: Path,
        collection_name: str,
        embedding_function: Any | None = None,
    ) -> None:
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        kwargs: dict[str, Any] = {"name": collection_name}
        if embedding_function is not None:
            # Injectable so tests can use a trivial deterministic embedder.
            kwargs["embedding_function"] = embedding_function
        self._collection = self._client.get_or_create_collection(**kwargs)

    def add(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0
        self._collection.upsert(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source, "index": c.index} for c in chunks],
        )
        return len(chunks)

    def query(self, text: str, k: int) -> list[dict[str, Any]]:
        res = self._collection.query(query_texts=[text], n_results=k)
        docs = res["documents"][0]
        metas = res["metadatas"][0]
        dists = res["distances"][0]
        return [
            {
                "text": doc,
                "source": meta.get("source"),
                "index": meta.get("index"),
                "distance": dist,
            }
            for doc, meta, dist in zip(docs, metas, dists)
        ]

    def count(self) -> int:
        return self._collection.count()
