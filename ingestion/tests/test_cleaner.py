from ingestion.cleaners import clean_text

DIRTY_TEXT = """Skip to main content
Home
# Fall Registration
Registration opens   on   July 6, 2026.
- See the calendar at https://example.edu/cal?utm_source=newsletter&utm_medium=email for details
Copyright © 2026 University of Illinois Springfield.
All rights reserved.
"""


def test_clean_text_drops_boilerplate_and_tracking_params_but_keeps_content():
    cleaned = clean_text(DIRTY_TEXT)

    assert "Skip to main content" not in cleaned
    assert "Home" not in cleaned.splitlines()
    assert "Copyright" not in cleaned
    assert "All rights reserved" not in cleaned

    # Real content, headings, and list markers are preserved
    assert "# Fall Registration" in cleaned
    assert "Registration opens on July 6, 2026." in cleaned  # whitespace collapsed
    assert "https://example.edu/cal" in cleaned
    assert "utm_source" not in cleaned
    assert "utm_medium" not in cleaned
