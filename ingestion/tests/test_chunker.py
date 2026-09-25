from ingestion.chunkers import approx_tokens, chunk_text

# 25 lines x 30 words ≈ 750 words ≈ 975 approx tokens — comfortably forces
# more than one chunk at the default 300-700 token target.
_LONG_TEXT = "\n".join(f"Paragraph {i} " + " ".join(["word"] * 29) for i in range(25))


def test_chunk_text_empty_returns_no_chunks():
    assert chunk_text("") == []


def test_chunk_text_splits_long_document_within_target_bounds():
    chunks = chunk_text(_LONG_TEXT, target_min_tokens=300, target_max_tokens=700, overlap_tokens=50)

    assert len(chunks) > 1
    # every chunk but possibly the last should be within/near the target band
    for chunk in chunks[:-1]:
        tokens = approx_tokens(chunk)
        assert 300 <= tokens <= 700 + 60  # small slack for the line that tipped it over

    # every source paragraph marker shows up somewhere in the chunks
    for i in range(25):
        assert any(f"Paragraph {i} " in chunk for chunk in chunks)


def test_chunk_text_short_document_is_a_single_chunk():
    short_text = "# Title\nOne short paragraph of a few words."
    chunks = chunk_text(short_text)

    assert len(chunks) == 1
    assert "# Title" in chunks[0]
