"""Tests for should_warn_idle (leaf-07).

Idle window assumption: 1800 seconds (30 min), matching leaf-04.
Warning window: 5 minutes (300 s) before idle.
"""
from src.session_warning import should_warn_idle
from src.types import Session


def _sess(last_active_ts: float) -> Session:
    return Session(session_id="s1", user_id="u1", last_active_ts=last_active_ts)


def test_active_session_does_not_warn():
    # 0 seconds elapsed — well within idle window, no warning.
    s = _sess(last_active_ts=1000.0)
    assert should_warn_idle(s, now_ts=1000.0) is False


def test_just_inside_warning_window_warns():
    # 1500 s elapsed = exactly 5 min before 1800 s idle threshold.
    s = _sess(last_active_ts=0.0)
    assert should_warn_idle(s, now_ts=1500.0) is True


def test_well_inside_warning_window_warns():
    # 1700 s elapsed = 100 s before idle.
    s = _sess(last_active_ts=0.0)
    assert should_warn_idle(s, now_ts=1700.0) is True


def test_just_before_warning_window_does_not_warn():
    # 1499 s elapsed = 1 s before warning window begins.
    s = _sess(last_active_ts=0.0)
    assert should_warn_idle(s, now_ts=1499.0) is False


def test_at_idle_threshold_does_not_warn():
    # 1800 s elapsed = already idle; cleanup territory, no warning.
    s = _sess(last_active_ts=0.0)
    assert should_warn_idle(s, now_ts=1800.0) is False


def test_past_idle_threshold_does_not_warn():
    # 3600 s elapsed = long past idle; no warning.
    s = _sess(last_active_ts=0.0)
    assert should_warn_idle(s, now_ts=3600.0) is False
