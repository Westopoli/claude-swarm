"""Session idle warning (leaf-07).

Idle window: 1800 s (matches leaf-04's cleanup threshold).
Warning window: 5 min (300 s) before idle.
"""
from src.types import Session

SESSION_IDLE_SECONDS: float = 1800.0
WARNING_WINDOW_SECONDS: float = 300.0


def should_warn_idle(session: Session, now_ts: float) -> bool:
    """Return True iff the session is within the 5-minute warning window
    leading up to the idle threshold, but not yet idle."""
    elapsed = now_ts - session.last_active_ts
    return (SESSION_IDLE_SECONDS - WARNING_WINDOW_SECONDS) <= elapsed < SESSION_IDLE_SECONDS
