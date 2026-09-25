from app.retrieval.keyword_search import tokenize

# Roadmap §10 intents. Substring phrases (not just single tokens) are
# matched against the lowercased query so multi-word cues like "add/drop"
# or "final exam" count as one hit.
CATEGORY_PHRASES: dict[str, set[str]] = {
    "registration": {
        "register",
        "registration",
        "enroll",
        "enrollment",
        "add/drop",
        "waitlist",
        "withdraw",
        "prerequisite",
        "credit hour",
    },
    "academic": {
        "calendar",
        "semester",
        "classes begin",
        "class begins",
        "break",
        "commencement",
        "final exam",
        "midterm",
        "academic year",
    },
    "library": {"library", "librarian", "database", "research guide", "book"},
    "event": {"event", "events"},
    "organization": {"organization", "organizations", "club", "clubs"},
    "policy": {"policy", "policies", "requirement", "requirements"},
    "department": {"department", "departments"},
    "administrative": {
        "form",
        "forms",
        "fee",
        "fees",
        "deadline",
        "deadlines",
        "graduation",
        "application",
    },
}


def classify(query: str) -> str:
    """Rule-based intent classification (roadmap §10) — deliberately not
    LLM-based; the LLM only enters the pipeline at generation time
    (Module 5)."""
    if not tokenize(query):
        return "unknown"

    lowered = query.lower()
    best_category = "general"
    best_hits = 0
    for category, phrases in CATEGORY_PHRASES.items():
        hits = sum(1 for phrase in phrases if phrase in lowered)
        if hits > best_hits:
            best_hits = hits
            best_category = category

    return best_category
