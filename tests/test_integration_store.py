"""End-to-end store test using a trivial deterministic embedder (no model download).

Marked `integration` only because it exercises Chroma's on-disk persistence; it
still avoids the network by injecting a hash-based embedding function.
"""

from __future__ import annotations

import numpy as np
import pytest
from chromadb.api.types import EmbeddingFunction

from ask_my_docs.chunking import chunk_document
from ask_my_docs.store import VectorStore

pytestmark = pytest.mark.integration

_DIM = 32


class HashEmbeddingFunction(EmbeddingFunction):
    """A toy embedding function: deterministic, offline, good enough for a smoke test.

    Subclasses Chroma's EmbeddingFunction so the query path (`embed_query`) and the
    config hooks resolve; `embed_query` defaults to `__call__`.
    """

    def __call__(self, input):  # noqa: A002 - Chroma's interface uses `input`
        vectors = []
        for doc in input:
            vec = [0.0] * _DIM
            for i, ch in enumerate(doc):
                vec[i % _DIM] += ord(ch)
            vectors.append(np.array(vec, dtype=np.float32))
        return vectors

    @staticmethod
    def name() -> str:
        return "hash-embedding"

    def get_config(self) -> dict:
        return {"dim": _DIM}

    @staticmethod
    def build_from_config(config: dict) -> "HashEmbeddingFunction":
        return HashEmbeddingFunction()


def test_ingest_and_query_roundtrip(tmp_path):
    store = VectorStore(
        persist_dir=tmp_path / "chroma",
        collection_name="test",
        embedding_function=HashEmbeddingFunction(),
    )

    chunks = chunk_document(
        "Pro costs forty nine dollars per user per month.",
        source="pricing.md",
        chunk_size=200,
        chunk_overlap=20,
    )
    chunks += chunk_document(
        "The free tier allows sixty requests per minute.",
        source="limits.md",
        chunk_size=200,
        chunk_overlap=20,
    )

    added = store.add(chunks)
    assert added == len(chunks)
    assert store.count() == len(chunks)

    results = store.query("how much does pro cost", k=2)
    assert results
    assert {r["source"] for r in results} <= {"pricing.md", "limits.md"}
