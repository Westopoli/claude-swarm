"""Tests for should_warn_idle (leaf-07)."""
from src.types import Session
from src.session_warning import should_warn_idle, SESSION_IDLE_TIMEOUT_SECONDS


def _make(last_active_ts: float) -> Session:
    return Session(session_id="s", user_id="u", last_active_ts=last_active_ts)


def test_fresh_session_does_not_warn():
    now = 10_000.0
    s = _make(last_active_ts=now - 60)  # 1 minute old
    assert should_warn_idle(s, now) is False


def test_session_just_inside_warning_window_warns():
    now = 10_000.0
    # Age = idle_timeout - 299 seconds → within 5 min of idle
    s = _make(last_active_ts=now - (SESSION_IDLE_TIMEOUT_SECONDS - 299))
    assert should_warn_idle(s, now) is True


def test_session_exactly_at_warning_boundary_warns():
    now = 10_000.0
    # Age = idle_timeout - 300 → exactly 5 min before idle
    s = _make(last_active_ts=now - (SESSION_IDLE_TIMEOUT_SECONDS - 300))
    assert should_warn_idle(s, now) is True


def test_session_just_outside_warning_window_does_not_warn():
    now = 10_000.0
    # Age = idle_timeout - 301 → just over 5 min before idle
    s = _make(last_active_ts=now - (SESSION_IDLE_TIMEOUT_SECONDS - 301))
    assert should_warn_idle(s, now) is False


def test_already_idle_session_does_not_warn():
    now = 10_000.0
    # Age == idle_timeout → already idle, not "within 5 min of" idle
    s = _make(last_active_ts=now - SESSION_IDLE_TIMEOUT_SECONDS)
    assert should_warn_idle(s, now) is False


def test_long_idle_session_does_not_warn():
    now = 10_000.0
    s = _make(last_active_ts=now - (SESSION_IDLE_TIMEOUT_SECONDS * 2))
    assert should_warn_idle(s, now) is False
