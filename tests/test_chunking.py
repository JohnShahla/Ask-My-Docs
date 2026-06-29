import pytest

from ask_my_docs.chunking import Chunk, chunk_document, split_text


def test_split_respects_chunk_size():
    text = "abcdefghij" * 10  # 100 chars
    chunks = split_text(text, chunk_size=40, chunk_overlap=10)
    assert chunks  # non-empty
    assert all(len(c) <= 40 for c in chunks)
    assert len(chunks) > 1


def test_split_starts_at_beginning():
    text = "".join(str(i % 10) for i in range(100))
    chunks = split_text(text, chunk_size=30, chunk_overlap=10)
    assert chunks[0].startswith(text[:5])


def test_split_short_text_single_chunk():
    chunks = split_text("hello world", chunk_size=100, chunk_overlap=10)
    assert chunks == ["hello world"]


def test_split_empty_text():
    assert split_text("   ", chunk_size=10, chunk_overlap=2) == []


def test_split_invalid_overlap():
    with pytest.raises(ValueError):
        split_text("hello", chunk_size=10, chunk_overlap=10)


def test_split_invalid_chunk_size():
    with pytest.raises(ValueError):
        split_text("hello", chunk_size=0, chunk_overlap=0)


def test_chunk_document_ids_and_type():
    chunks = chunk_document("a" * 50, source="x.md", chunk_size=20, chunk_overlap=5)
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].id == "x.md::0"
    assert chunks[1].id == "x.md::1"
