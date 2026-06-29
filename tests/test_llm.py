from ask_my_docs.llm import build_user_prompt, format_context


def _contexts():
    return [
        {"source": "a.md", "text": "Pro costs $49 per user per month."},
        {"source": "b.md", "text": "Free tier allows 60 requests per minute."},
    ]


def test_format_context_includes_sources():
    out = format_context(_contexts())
    assert "[a.md]" in out
    assert "[b.md]" in out
    assert "$49" in out


def test_build_user_prompt_with_context():
    prompt = build_user_prompt("How much is Pro?", _contexts())
    assert "How much is Pro?" in prompt
    assert "[a.md]" in prompt


def test_build_user_prompt_without_context():
    prompt = build_user_prompt("Anything?", [])
    assert "none retrieved" in prompt
    assert "Anything?" in prompt
