"""Load documents from a directory, chunk them, and write them to the vector store."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

from .chunking import chunk_document
from .config import Settings
from .store import VectorStore

SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf"}


def load_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8")


def iter_documents(source_dir: Path) -> Iterator[Path]:
    for path in sorted(source_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path


def ingest_directory(
    source_dir: Path, store: VectorStore, settings: Settings
) -> dict[str, int]:
    """Ingest every supported file under ``source_dir``. Returns a small summary."""
    files = 0
    total_chunks = 0
    for path in iter_documents(source_dir):
        text = load_text(path)
        chunks = chunk_document(
            text,
            source=path.name,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        store.add(chunks)
        files += 1
        total_chunks += len(chunks)
    return {"files": files, "chunks": total_chunks}
