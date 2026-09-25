import json
import logging
import sys

logger = logging.getLogger("campusai")
logger.setLevel(logging.INFO)

if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)


def log_event(event: str, **fields) -> None:
    """One structured JSON line per event — roadmap §35: query, intent,
    retrieved doc ids/scores, latency, verification result. A real
    observability backend (e.g. Langfuse) would read this stream or
    replace this function's body; not a hard dependency for this
    portfolio project (see docs/PROJECT_CONTRACT.md Module 6)."""
    logger.info(json.dumps({"event": event, **fields}, default=str))
