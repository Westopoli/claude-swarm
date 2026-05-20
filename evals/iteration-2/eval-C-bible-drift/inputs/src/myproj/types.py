"""Shared type contract for myproj. Parent-owned. No leaf edits this file."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultRow:
    keys: dict[str, str]
    metrics: dict[str, float]
