from evaluation.metrics import hit_rate, mean_reciprocal_rank, precision_at_k, recall_at_k

PAIRS = [
    (["a", "b", "c"], "a"),  # rank 1
    (["b", "a", "c"], "a"),  # rank 2
    (["b", "c", "d"], "a"),  # miss
]


def test_recall_at_k_counts_any_rank_as_a_hit():
    assert recall_at_k(PAIRS) == 2 / 3


def test_recall_at_k_empty_is_zero():
    assert recall_at_k([]) == 0.0


def test_mean_reciprocal_rank_weights_earlier_ranks_higher():
    expected = (1 / 1 + 1 / 2 + 0) / 3
    assert mean_reciprocal_rank(PAIRS) == expected


def test_precision_at_k_single_relevant_doc_per_query():
    # each query has exactly one relevant doc, so precision@3 is 1/3 on a
    # hit (regardless of its rank within the top 3) and 0 on a miss
    expected = (1 / 3 + 1 / 3 + 0) / 3
    assert precision_at_k(PAIRS, k=3) == expected


def test_hit_rate_counts_nonempty_results_regardless_of_correctness():
    pairs_with_wrong_but_nonempty = [(["z"], "a"), ([], "a")]
    assert hit_rate(pairs_with_wrong_but_nonempty) == 0.5
