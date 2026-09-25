from app.retrieval.access_control import filter_by_role
from app.retrieval.vector_search import SearchResult


def _result(chunk_id: str, access_level: str) -> SearchResult:
    return SearchResult(
        score=1.0,
        chunk_id=chunk_id,
        document_id=chunk_id,
        title="Title",
        content="content",
        url="https://example.edu",
        source="Test",
        department="Test",
        document_type="test",
        access_level=access_level,
        version="1.0",
    )


def test_student_sees_public_but_not_authorized():
    results = [_result("pub", "public"), _result("auth", "authorized")]

    filtered = filter_by_role(results, ["student"])

    assert [r.chunk_id for r in filtered] == ["pub"]


def test_staff_sees_both_public_and_authorized():
    results = [_result("pub", "public"), _result("auth", "authorized")]

    filtered = filter_by_role(results, ["staff"])

    assert {r.chunk_id for r in filtered} == {"pub", "auth"}


def test_restricted_is_never_visible_to_any_role():
    results = [_result("restricted", "restricted")]

    for role in ["student", "faculty", "staff", "admin"]:
        assert filter_by_role(results, [role]) == []


def test_unknown_access_level_denies_by_default():
    results = [_result("weird", "some_future_level")]

    assert filter_by_role(results, ["admin"]) == []
