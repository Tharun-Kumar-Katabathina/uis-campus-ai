import re

# Lines that are pure boilerplate noise once the extractor has already
# stripped nav/header/footer tags — leftover skip links, repeated menu
# labels, and tracking-parameter-only fragments.
_BOILERPLATE_PATTERNS = [
    re.compile(r"^skip to (main )?content$", re.IGNORECASE),
    re.compile(r"^(home|menu|search)$", re.IGNORECASE),
    re.compile(r"^copyright ©.*$", re.IGNORECASE),
    re.compile(r"^all rights reserved\.?$", re.IGNORECASE),
]

_TRACKING_PARAM_RE = re.compile(r"[?&](utm_[a-z]+|fbclid|gclid)=[^&\s]+", re.IGNORECASE)


def clean_text(raw: str) -> str:
    """Normalize extracted text: drop boilerplate lines, strip tracking
    query params from URLs, collapse whitespace. Preserves heading markers
    (`#`), list markers (`-`), and URLs (roadmap §19)."""
    lines = []
    for line in raw.splitlines():
        line = _TRACKING_PARAM_RE.sub("", line)
        line = " ".join(line.split())
        if not line:
            continue
        if any(pattern.match(line) for pattern in _BOILERPLATE_PATTERNS):
            continue
        lines.append(line)

    return "\n".join(lines)
