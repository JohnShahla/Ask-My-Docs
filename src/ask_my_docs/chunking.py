"""Deterministic, dependency-free text chunking.

Kept pure (no I/O, no models) so it's fast to unit-test and easy to reason about.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    index: int

    @property
    def id(self) -> str:
        # Stable id → re-ingesting the same file upserts in place instead of duplicating.
        return f"{self.source}::{self.index}"


def split_text(text: str, *, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into overlapping windows of at most ``chunk_size`` characters."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    step = chunk_size - chunk_overlap
    chunks: list[str] = []
    for start in range(0, len(text), step):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(piece)
        if start + chunk_size >= len(text):
            break
    return chunks


def chunk_document(
    text: str, source: str, *, chunk_size: int, chunk_overlap: int
) -> list[Chunk]:
    """Split a document into :class:`Chunk` objects tagged with their source."""
    pieces = split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [Chunk(text=t, source=source, index=i) for i, t in enumerate(pieces)]
