"""The regression gate: CI fails the build if any score drops below its
floor. Floors are set with margin below the measured baseline (see
evaluation/README.md) so real regressions get caught without flakiness
from the small dataset's natural variance."""

from evaluate import run

REPORT = run()  # module-level: computed once, real embedder + real corpus


def test_recall_at_3_floor():
    assert REPORT.recall_at_3 >= 0.85, REPORT.summary()


def test_precision_at_3_floor():
    assert REPORT.precision_at_3 >= 0.25, REPORT.summary()


def test_mrr_floor():
    assert REPORT.mrr >= 0.75, REPORT.summary()


def test_hit_rate_floor():
    assert REPORT.hit_rate >= 0.95, REPORT.summary()


def test_faithfulness_rate_floor():
    assert REPORT.faithfulness_rate >= 0.9, REPORT.summary()


def test_citation_correctness_rate_floor():
    assert REPORT.citation_correctness_rate >= 0.95, REPORT.summary()


def test_hallucination_catch_rate_floor():
    assert REPORT.hallucination_catch_rate >= 0.9, REPORT.summary()


def test_abstention_quality_floor():
    assert REPORT.abstention_quality >= 0.8, REPORT.summary()
