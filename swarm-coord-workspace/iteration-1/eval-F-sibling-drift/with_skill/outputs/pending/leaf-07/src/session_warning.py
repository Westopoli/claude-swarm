"""leaf-07 — session idle-warning predicate.

Returns True when a session is within the warning window of becoming idle.
The idle threshold matches leaf-04's cleanup function (sibling-assumption
read: 1800 s / 30 min). See .swarm/briefs/leaf-07.ASSUMPTIONS.md.
"""
from src.types import Session

# Idle window — matches leaf-04 (see leaf-07.ASSUMPTIONS.md).
SESSION_IDLE_TIMEOUT_SECONDS: int = 1800

# Warning window — "within 5 minutes of being considered idle" (brief).
WARNING_WINDOW_SECONDS: int = 300


def should_warn_idle(session: Session, now_ts: float) -> bool:
    """Return True iff `session` is within WARNING_WINDOW_SECONDS of idle.

    Semantics: True when
        SESSION_IDLE_TIMEOUT_SECONDS - WARNING_WINDOW_SECONDS
            <= age
            < SESSION_IDLE_TIMEOUT_SECONDS
    where age = now_ts - session.last_active_ts. At/after idle_timeout the
    session is already idle (leaf-04's cleanup domain) so warning no longer
    applies.
    """
    age = now_ts - session.last_active_ts
    if age < 0:
        return False
    warn_start = SESSION_IDLE_TIMEOUT_SECONDS - WARNING_WINDOW_SECONDS
    return warn_start <= age < SESSION_IDLE_TIMEOUT_SECONDS
