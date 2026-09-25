import json
from pathlib import Path

from ingestion import pipeline

HTML_TEMPLATE = """
<html><body><main>
<h1>{title}</h1>
<p>{body}</p>
</main></body></html>
"""


def _write_manifest(tmp_path: Path, entries: list[dict]) -> Path:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(entries))
    return manifest_path


def _entry(document_id: str, path: str, **overrides) -> dict:
    base = {
        "document_id": document_id,
        "type": "html",
        "path": path,
        "title": document_id,
        "source": "Test Source",
        "department": "Test Dept",
        "document_type": "test",
        "url": "https://example.edu/test",
        "access_level": "public",
        "version": "1.0",
    }
    base.update(overrides)
    return base


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_pipeline_end_to_end_over_sample_sources(tmp_path: Path):
    output_path = tmp_path / "chunks.jsonl"
    state_path = tmp_path / "state.json"

    result = pipeline.run(
        manifest_path=pipeline.DEFAULT_MANIFEST,
        raw_dir=pipeline.DEFAULT_RAW_DIR,
        output_path=output_path,
        state_path=state_path,
    )

    assert output_path.exists()
    records = _read_jsonl(output_path)
    assert len(records) == result.chunk_count
    assert result.chunk_count > 0

    for record in records:
        assert record["document_id"]
        assert record["chunk_id"]
        assert record["content"]
        assert record["access_level"] == "public"

    # the restricted sample source must never reach the output
    assert all(r["document_id"] != "staff_payroll_records" for r in records)
    assert any(doc_id == "staff_payroll_records" for doc_id, _ in result.skipped_restricted)


def test_pipeline_change_detection_is_isolated_per_document(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "a.html").write_text(HTML_TEMPLATE.format(title="Doc A", body="Original content A."))
    (raw_dir / "b.html").write_text(HTML_TEMPLATE.format(title="Doc B", body="Original content B."))

    manifest_path = _write_manifest(
        tmp_path,
        [_entry("doc_a", "a.html"), _entry("doc_b", "b.html")],
    )
    output_path = tmp_path / "chunks.jsonl"
    state_path = tmp_path / "state.json"

    # First run: both documents are new.
    result1 = pipeline.run(manifest_path, raw_dir, output_path, state_path)
    assert set(result1.processed) == {"doc_a", "doc_b"}
    assert result1.skipped_unchanged == []
    first_output = output_path.read_text()

    # Second run, nothing changed: both should be skipped as unchanged and
    # output must be byte-for-byte identical.
    result2 = pipeline.run(manifest_path, raw_dir, output_path, state_path)
    assert result2.processed == []
    assert set(result2.skipped_unchanged) == {"doc_a", "doc_b"}
    assert output_path.read_text() == first_output

    # Third run, only doc_a's content changes: only doc_a should be
    # reprocessed and version-bumped; doc_b's chunks/version must be
    # untouched.
    (raw_dir / "a.html").write_text(HTML_TEMPLATE.format(title="Doc A", body="Updated content A!"))
    result3 = pipeline.run(manifest_path, raw_dir, output_path, state_path)
    assert result3.processed == ["doc_a"]
    assert result3.skipped_unchanged == ["doc_b"]

    state = json.loads(state_path.read_text())
    assert state["doc_a"]["version"] == "1.1"
    assert state["doc_b"]["version"] == "1.0"

    records = _read_jsonl(output_path)
    doc_a_records = [r for r in records if r["document_id"] == "doc_a"]
    doc_b_records = [r for r in records if r["document_id"] == "doc_b"]
    assert all(r["version"] == "1.1" for r in doc_a_records)
    assert any("Updated content A!" in r["content"] for r in doc_a_records)
    assert all(r["version"] == "1.0" for r in doc_b_records)
    assert any("Original content B." in r["content"] for r in doc_b_records)
