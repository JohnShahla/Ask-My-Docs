"""Answer generation with Claude, grounded in retrieved context."""

from __future__ import annotations

from typing import Any

import anthropic

SYSTEM_PROMPT = (
    "You are a precise documentation assistant. Answer the user's question using ONLY the "
    "provided context passages. After each claim, cite the source filename in square brackets, "
    "e.g. [orbit-handbook.md]. If the answer is not contained in the context, say you don't "
    "know — never invent information."
)


def format_context(contexts: list[dict[str, Any]]) -> str:
    return "\n\n---\n\n".join(f"[{c['source']}]\n{c['text']}" for c in contexts)


def build_user_prompt(question: str, contexts: list[dict[str, Any]]) -> str:
    if not contexts:
        return f"Context passages:\n(none retrieved)\n\nQuestion: {question}"
    return f"Context passages:\n\n{format_context(contexts)}\n\nQuestion: {question}"


def generate_answer(
    client: anthropic.Anthropic,
    model: str,
    question: str,
    contexts: list[dict[str, Any]],
    max_tokens: int,
) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(question, contexts)}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()
