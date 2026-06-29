"""The RAG pipeline: retrieve relevant chunks, then answer grounded in them."""

from __future__ import annotations

from typing import Any

import anthropic

from .config import Settings
from .llm import generate_answer
from .store import VectorStore


def answer_question(
    question: str,
    store: VectorStore,
    client: anthropic.Anthropic,
    settings: Settings,
    k: int | None = None,
) -> dict[str, Any]:
    k = k or settings.top_k
    contexts = store.query(question, k=k)
    answer = generate_answer(
        client,
        settings.answer_model,
        question,
        contexts,
        settings.max_answer_tokens,
    )

    sources: list[str] = []
    for c in contexts:
        if c["source"] not in sources:
            sources.append(c["source"])

    return {"answer": answer, "sources": sources, "contexts": contexts}
