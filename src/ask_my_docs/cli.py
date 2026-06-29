"""Command-line interface: `ask-my-docs ingest` and `ask-my-docs ask`."""

from __future__ import annotations

import os
from pathlib import Path

import anthropic
import typer
from rich.console import Console
from rich.panel import Panel

from .config import PROJECT_ROOT, settings
from .ingest import ingest_directory
from .rag import answer_question
from .store import VectorStore

app = typer.Typer(
    help="Ask-My-Docs: a small, production-minded RAG over your documents.",
    no_args_is_help=True,
)
console = Console()


def _store() -> VectorStore:
    return VectorStore(settings.persist_dir, settings.collection_name)


@app.command()
def ingest(
    source: Path = typer.Argument(
        PROJECT_ROOT / "data" / "sample_docs",
        help="Directory of .md / .txt / .pdf files to index.",
    ),
) -> None:
    """Chunk and embed documents into the vector store."""
    store = _store()
    console.print(f"Ingesting from [bold]{source}[/bold] …")
    result = ingest_directory(source, store, settings)
    console.print(
        f"Indexed [green]{result['chunks']}[/green] chunks from "
        f"[green]{result['files']}[/green] file(s). "
        f"Collection size: {store.count()}"
    )


@app.command()
def ask(
    question: str = typer.Argument(..., help="The question to answer."),
    k: int = typer.Option(settings.top_k, help="Number of passages to retrieve."),
) -> None:
    """Answer a question against the indexed documents."""
    store = _store()
    if store.count() == 0:
        console.print("[red]No documents indexed.[/red] Run `ask-my-docs ingest` first.")
        raise typer.Exit(code=1)

    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(
            "[red]ANTHROPIC_API_KEY is not set.[/red] "
            "Copy .env.example to .env and add your key (see the README)."
        )
        raise typer.Exit(code=1)

    client = anthropic.Anthropic()
    result = answer_question(question, store, client, settings, k=k)
    console.print(Panel(result["answer"], title="Answer", border_style="green"))
    console.print(f"[dim]Sources: {', '.join(result['sources'])}[/dim]")


if __name__ == "__main__":
    app()
