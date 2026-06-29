# Ask-My-Docs

[![CI](https://github.com/JohnShahla/Ask-My-Docs/actions/workflows/ci.yml/badge.svg)](https://github.com/JohnShahla/Ask-My-Docs/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A small retrieval-augmented generation (RAG) system that answers questions about
your own documents. It ships with an evaluation harness, because "it returned an
answer" and "the answer was actually correct and grounded" are two different things.

Point it at a folder of `.md` / `.txt` / `.pdf` files, ingest them, then ask
questions. Answers are grounded in the retrieved passages and cite their source
files; if something isn't in your docs, it says so instead of making it up.

```
$ ask-my-docs ask "How much does the Orbit Pro plan cost?"
╭───────────────────────────── Answer ─────────────────────────────╮
│ The Orbit Pro plan costs $49 per user per month. [orbit-handbook.md] │
╰───────────────────────────────────────────────────────────────────╯
Sources: orbit-handbook.md
```

## How it works

```
documents ──▶ chunk ──▶ embed (local) ──▶ Chroma vector store
                                                │
                    question ──▶ retrieve top-k ─┤
                                                ▼
                                     Claude (grounded answer + citations)
```

Embeddings run locally (sentence-transformers via Chroma), so the index needs no
API key. The only part that calls a model is answering and evaluation. There's a
fuller diagram and a module-by-module breakdown in
[docs/architecture.md](docs/architecture.md).

## Setup

```bash
pip install -e ".[dev]"
```

Answering and the eval harness call Claude, so you need an Anthropic API key:

```bash
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

`.env` is gitignored, so the key never gets committed. You can also just export
`ANTHROPIC_API_KEY` in your shell instead of using a file.

> Heads up: the first `ingest` (or `ask`) downloads the local embedding model the
> first time it runs (~80 MB). After that it's cached.

## Usage

```bash
# index the bundled sample docs, or point it at your own folder
ask-my-docs ingest
ask-my-docs ingest /path/to/your/docs

ask-my-docs ask "What is the API rate limit on the Free tier?"
ask-my-docs ask "Is Orbit SOC 2 compliant?" --k 6
```

## Evaluation

This is the part I cared most about. Retrieval and generation are scored
separately:

```bash
python evals/run_evals.py
```

```
                         RAG Evaluation
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
┃ # ┃ Question                          ┃ Hit@k ┃ RR ┃ Faithful ┃ Relevant ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
│ 1 │ How much does the Orbit Pro plan… │  ✅   │1.00│   ✅     │   ✅     │
│ … │                                   │       │    │          │          │
└───┴───────────────────────────────────┴───────┴────┴──────────┴──────────┘

Hit@k: 100%   MRR: 0.92   Faithfulness: 100%   Answer relevance: 100%
```

- Retrieval is scored with `hit@k` and mean reciprocal rank against a labeled
  question set. Those are plain functions (`metrics.py`), so they're deterministic
  and unit-tested — no model calls.
- Answer quality (faithfulness, relevance) uses Claude as a judge with structured
  output, so the verdict always parses back into a typed object.

More detail, and how to grow the dataset, is in [evals/README.md](evals/README.md).

## Development

```bash
ruff check .                  # lint
pytest -m "not integration"   # fast unit tests (this is what CI runs)
RUN_INTEGRATION=1 pytest      # also exercises the Chroma store end to end
```

CI runs lint + the unit tests on every push (`.github/workflows/ci.yml`).

## Layout

```
src/ask_my_docs/   chunking · store · ingest · llm · rag · metrics · cli · config
evals/             dataset.jsonl + run_evals.py
data/sample_docs/  a couple of fictional "Orbit Analytics" docs to try it out
tests/             unit tests + one opt-in integration test
docs/              architecture notes
```

## Built with

Python, the Anthropic SDK, ChromaDB, Typer, Rich, Pydantic, pytest, Ruff, GitHub
Actions.

## License

MIT
