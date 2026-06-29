# Evaluation harness

This is the part most RAG demos skip — and the part that signals real AI
engineering. It measures two things separately:

## 1. Retrieval quality (deterministic)

`metrics.py` computes, from a labeled set of `(question → relevant source)` pairs:

- **Hit@k** — did at least one retrieved chunk come from a relevant document?
- **MRR** (mean reciprocal rank) — how highly was the first relevant chunk ranked?

These are pure functions with no model calls, so they're fast, free, and unit-tested.

## 2. Answer quality (LLM-as-judge)

`run_evals.py` uses a separate Claude call to grade each generated answer for:

- **Faithfulness** — every claim is grounded in the retrieved context (no hallucination).
- **Relevance** — the answer actually addresses the question.

The judge returns **structured output** (a Pydantic `Judgement`), so the verdict is
always parseable — no brittle string scraping.

## Running

```bash
ask-my-docs ingest          # index the sample docs first
python evals/run_evals.py    # needs ANTHROPIC_API_KEY
```

## Extending

- Add rows to `dataset.jsonl`: `{"question": "...", "relevant_sources": ["file.md"]}`.
- Add chunk-level labels for precision/recall instead of document-level hit@k.
- Track scores over time (commit a JSON report per run) to catch regressions when
  you change the chunker, `top_k`, or the embedding model.
