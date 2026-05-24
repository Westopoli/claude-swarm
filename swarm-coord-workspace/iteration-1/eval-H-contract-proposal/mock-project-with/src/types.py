"""Parent-owned types. Do not edit from leaf agents."""
from dataclasses import dataclass


@dataclass
class Session:
    user_id: str
    last_seen: int
