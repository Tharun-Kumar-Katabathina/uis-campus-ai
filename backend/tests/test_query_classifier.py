import pytest

from app.retrieval.query_classifier import classify


@pytest.mark.parametrize(
    "query,expected",
    [
        ("When does fall registration open?", "registration"),
        ("When do classes begin this semester?", "academic"),
        ("What are the library hours?", "library"),
        ("What campus events are happening this week?", "event"),
        ("How do I join a student organization?", "organization"),
        ("What is the grading policy?", "policy"),
        ("Who is in the Computer Science department?", "department"),
        ("Where do I submit the graduation application form?", "administrative"),
        ("What's your favorite color?", "general"),
        ("", "unknown"),
    ],
)
def test_classify(query: str, expected: str):
    assert classify(query) == expected
