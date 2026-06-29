"""Evaluate the RAG pipeline on a labeled question set.

Two layers of evaluation:

1. Retrieval quality (deterministic) — hit@k and mean reciprocal rank, computed
   from labeled relevant sources. No model judgment, no flakiness.
2. Answer quality (LLM-as-judge) — a separate Claude call grades each answer for
   faithfulness (grounded in the retrieved context) and relevance (addresses the
   question), using structured output so the verdict is always parseable.

Run:  python evals/run_evals.py   (after `ask-my-docs ingest`)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import anthropic
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from ask_my_docs.config import settings
from ask_my_docs.metrics import hit, reciprocal_rank
from ask_my_docs.rag import answer_question
from ask_my_docs.store import VectorStore

console = Console()
DATASET = Path(__file__).parent / "dataset.jsonl"


class Judgement(BaseModel):
    faithful: bool  # every claim in the answer is supported by the context
    relevant: bool  # the answer actually addresses the question
    reasoning: str


JUDGE_SYSTEM = (
    "You are a strict evaluator of retrieval-augmented answers. Given a question, the "
    "retrieved context, and a candidate answer, decide whether the answer is FAITHFUL "
    "(every factual claim is supported by the context) and RELEVANT (it addresses the "
    "question). Be rigorous: an answer that adds unsupported facts is not faithful."
)


def load_dataset() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with DATASET.open() as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def judge(
    client: anthropic.Anthropic, question: str, contexts: list[dict[str, Any]], answer: str
) -> Judgement:
    ctx = "\n\n---\n\n".join(f"[{c['source']}]\n{c['text']}" for c in contexts)
    prompt = f"Question:\n{question}\n\nContext:\n{ctx}\n\nAnswer:\n{answer}"
    response = client.messages.parse(
        model=settings.judge_model,
        max_tokens=512,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_format=Judgement,
    )
    return response.parsed_output


def main() -> None:
    store = VectorStore(settings.persist_dir, settings.collection_name)
    if store.count() == 0:
        console.print("[red]No documents indexed.[/red] Run `ask-my-docs ingest` first.")
        raise SystemExit(1)

    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(
            "[red]ANTHROPIC_API_KEY is not set.[/red] "
            "Copy .env.example to .env and add your key (see the README)."
        )
        raise SystemExit(1)

    client = anthropic.Anthropic()
    items = load_dataset()

    table = Table(title="RAG Evaluation")
    table.add_column("#", justify="right")
    table.add_column("Question")
    table.add_column("Hit@k", justify="center")
    table.add_column("RR", justify="center")
    table.add_column("Faithful", justify="center")
    table.add_column("Relevant", justify="center")

    hits: list[bool] = []
    rrs: list[float] = []
    faiths: list[bool] = []
    rels: list[bool] = []

    for i, item in enumerate(items, start=1):
        result = answer_question(item["question"], store, client, settings)
        retrieved = [c["source"] for c in result["contexts"]]
        h = hit(retrieved, item["relevant_sources"])
        rr = reciprocal_rank(retrieved, item["relevant_sources"])
        verdict = judge(client, item["question"], result["contexts"], result["answer"])

        hits.append(h)
        rrs.append(rr)
        faiths.append(verdict.faithful)
        rels.append(verdict.relevant)

        table.add_row(
            str(i),
            item["question"][:50],
            "✅" if h else "❌",
            f"{rr:.2f}",
            "✅" if verdict.faithful else "❌",
            "✅" if verdict.relevant else "❌",
        )

    console.print(table)

    n = len(items)
    console.print(
        f"\n[bold]Hit@k:[/bold] {sum(hits) / n:.0%}   "
        f"[bold]MRR:[/bold] {sum(rrs) / n:.2f}   "
        f"[bold]Faithfulness:[/bold] {sum(faiths) / n:.0%}   "
        f"[bold]Answer relevance:[/bold] {sum(rels) / n:.0%}"
    )


if __name__ == "__main__":
    main()
