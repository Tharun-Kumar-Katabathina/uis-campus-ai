from pathlib import Path

from bs4 import BeautifulSoup


def extract_html(path: Path) -> str:
    """Extract structure-preserving plain text from an HTML file.

    Headings, list items, and paragraphs are each emitted on their own
    line so the cleaner/chunker downstream can reason about structure.
    Navigation/boilerplate elements (nav, header, footer, script, style,
    aside) are dropped before extraction.
    """
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(["nav", "header", "footer", "script", "style", "aside"]):
        tag.decompose()

    lines: list[str] = []
    body = soup.body or soup
    for element in body.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = " ".join(element.get_text().split())
        if not text:
            continue
        if element.name in {"h1", "h2", "h3", "h4"}:
            lines.append(f"{'#' * int(element.name[1])} {text}")
        elif element.name == "li":
            lines.append(f"- {text}")
        else:
            lines.append(text)

    return "\n".join(lines)
