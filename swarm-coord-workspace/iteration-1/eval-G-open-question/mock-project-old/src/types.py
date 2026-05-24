"""Parent-owned type contract."""
from dataclasses import dataclass


@dataclass
class Widget:
    name: str
    value: int
