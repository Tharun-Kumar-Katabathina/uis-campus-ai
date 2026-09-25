from app.retrieval.vector_search import SearchResult

# Roadmap §8-9: "public" documents are visible to every authenticated
# role; "authorized" documents (approved internal docs, department/staff
# resources) are visible only to non-student roles. "restricted" content
# is never ingested (see docs/PROJECT_CONTRACT.md Module 1 AC7), but is
# listed here so filtering still defaults closed if it ever appeared.
ACCESS_LEVEL_ALLOWED_ROLES: dict[str, frozenset[str]] = {
    "public": frozenset({"student", "faculty", "staff", "admin"}),
    "authorized": frozenset({"faculty", "staff", "admin"}),
    "restricted": frozenset(),
}


def filter_by_role(results: list[SearchResult], roles: list[str]) -> list[SearchResult]:
    """Drops any result none of `roles` is allowed to see, based on its
    access_level. An empty/missing access_level allow-list denies by
    default rather than silently letting it through."""
    role_set = set(roles)
    return [
        r for r in results if role_set & ACCESS_LEVEL_ALLOWED_ROLES.get(r.access_level, frozenset())
    ]
