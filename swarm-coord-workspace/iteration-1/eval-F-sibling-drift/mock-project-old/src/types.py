"""Locked type contract — parent-owned. Do not edit from leaf code."""
from dataclasses import dataclass


@dataclass
class Session:
    session_id: str
    user_id: str
    last_active_ts: float  # unix seconds
