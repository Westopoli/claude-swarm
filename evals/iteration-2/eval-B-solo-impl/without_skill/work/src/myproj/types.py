"""Shared type contract for myproj. Parent-owned. No leaf edits this file."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AggregatedRow:
    bucket_id: str
    value: float


@dataclass(frozen=True)
class WindowSpec:
    start: int
    end: int
    bucket_size: int
