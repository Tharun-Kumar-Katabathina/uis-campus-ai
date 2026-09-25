from app.retrieval.keyword_search import KeywordIndex, tokenize

RECORDS = [
    {
        "chunk_id": "doc_a_chunk_000",
        "document_id": "doc_a",
        "title": "Library Hours",
        "content": "The library is open Monday through Thursday from 8am to 11pm.",
        "url": "https://example.edu/library",
        "source": "Test",
        "department": "Library",
        "document_type": "library_hours",
        "access_level": "public",
        "version": "1.0",
    },
    {
        "chunk_id": "doc_b_chunk_000",
        "document_id": "doc_b",
        "title": "Academic Calendar",
        "content": "Fall registration opens in July. Classes begin in August.",
        "url": "https://example.edu/calendar",
        "source": "Test",
        "department": "Registrar",
        "document_type": "academic_calendar",
        "access_level": "public",
        "version": "1.0",
    },
    {
        "chunk_id": "doc_c_chunk_000",
        "document_id": "doc_c",
        "title": "Student Organizations",
        "content": "Students can join clubs through the involvement fair each fall.",
        "url": "https://example.edu/organizations",
        "source": "Test",
        "department": "Student Life",
        "document_type": "student_organizations",
        "access_level": "public",
        "version": "1.0",
    },
]


def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("Library Hours: Mon-Thu!") == ["library", "hours", "mon", "thu"]


def test_keyword_search_finds_lexical_match():
    index = KeywordIndex(RECORDS)
    results = index.search("library hours", top_k=5)

    assert len(results) == 1
    assert results[0].document_id == "doc_a"


def test_keyword_search_excludes_zero_score_documents():
    index = KeywordIndex(RECORDS)
    results = index.search("xylophone quantum", top_k=5)

    assert results == []


def test_keyword_search_respects_filters():
    index = KeywordIndex(RECORDS)
    # "registration" only appears in doc_b, but filter to doc_a's type
    results = index.search("registration", top_k=5, filters={"document_type": "library_hours"})

    assert results == []


def test_keyword_search_empty_corpus_returns_no_results():
    index = KeywordIndex([])
    assert index.search("anything") == []
