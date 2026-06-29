from ask_my_docs.metrics import hit, reciprocal_rank


def test_hit_true_when_relevant_retrieved():
    assert hit(["a.md", "b.md"], ["b.md"]) is True


def test_hit_false_when_none_relevant():
    assert hit(["a.md", "c.md"], ["b.md"]) is False


def test_reciprocal_rank_first_position():
    assert reciprocal_rank(["b.md", "a.md"], ["b.md"]) == 1.0


def test_reciprocal_rank_second_position():
    assert reciprocal_rank(["a.md", "b.md"], ["b.md"]) == 0.5


def test_reciprocal_rank_no_match():
    assert reciprocal_rank(["a.md", "c.md"], ["b.md"]) == 0.0
