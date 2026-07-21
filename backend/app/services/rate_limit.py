import time

_attempts: dict[str, list[float]] = {}


def is_rate_limited(key: str, max_attempts: int = 5, window_seconds: int = 900) -> bool:
    """In-memory sliding-window limiter keyed by anything (typically client IP). No Redis needed
    at this scale - a single backend process is the only place attempts are ever recorded.
    Returns True (blocked) BEFORE recording the current attempt, so callers should only call
    record_attempt() for attempts that actually happened (e.g. a failed passphrase/login)."""
    now = time.monotonic()
    recent = [t for t in _attempts.get(key, []) if now - t < window_seconds]
    _attempts[key] = recent
    return len(recent) >= max_attempts


def record_attempt(key: str) -> None:
    _attempts.setdefault(key, []).append(time.monotonic())
