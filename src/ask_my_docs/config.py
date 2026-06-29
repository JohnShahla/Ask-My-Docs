"""Centralized configuration, loaded from the environment (and a local .env)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Runtime settings. Override any value via an environment variable."""

    # Where Chroma persists its index on disk.
    persist_dir: Path = Path(os.getenv("CHROMA_DIR", str(PROJECT_ROOT / ".chroma")))
    collection_name: str = os.getenv("COLLECTION_NAME", "ask_my_docs")

    # Generation + evaluation models. Defaults to the latest Claude Opus.
    answer_model: str = os.getenv("ANSWER_MODEL", "claude-opus-4-8")
    judge_model: str = os.getenv("JUDGE_MODEL", "claude-opus-4-8")

    # Retrieval + chunking knobs.
    top_k: int = int(os.getenv("TOP_K", "4"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    max_answer_tokens: int = int(os.getenv("MAX_ANSWER_TOKENS", "1024"))


settings = Settings()
