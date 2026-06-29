"""Retrieval metrics. Pure functions — the testable core of the eval harness."""

from __future__ import annotations

from typing import Iterable


def hit(retrieved_sources: Iterable[str], relevant_sources: Iterable[str]) -> bool:
    """True if any retrieved source is in the relevant set (a.k.a. hit@k)."""
    relevant = set(relevant_sources)
    return any(s in relevant for s in retrieved_sources)


def reciprocal_rank(
    retrieved_sources: Iterable[str], relevant_sources: Iterable[str]
) -> float:
    """1/rank of the first relevant source, or 0.0 if none was retrieved."""
    relevant = set(relevant_sources)
    for rank, source in enumerate(retrieved_sources, start=1):
        if source in relevant:
            return 1.0 / rank
    return 0.0
