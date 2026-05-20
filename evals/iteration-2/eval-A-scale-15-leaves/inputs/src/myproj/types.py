"""Shared type contract for myproj. Parent-owned. No leaf edits this file."""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AggregatedRow:
    bucket_id: str
    value: float


@dataclass(frozen=True)
class WindowSpec:
    start: int
    end: int
    bucket_size: int


@dataclass(frozen=True)
class RollupKey:
    dimension: str
    value: str


@dataclass(frozen=True)
class DashboardView:
    name: str
    rows: list[AggregatedRow]


@dataclass(frozen=True)
class FilterPredicate:
    field: str
    op: Literal["eq", "ne", "gt", "lt", "in"]
    value: object


@dataclass(frozen=True)
class MetricDef:
    name: str
    aggregation: Literal["sum", "avg", "min", "max", "count"]


@dataclass(frozen=True)
class TimeRange:
    start_ts: int
    end_ts: int


@dataclass(frozen=True)
class BucketSize:
    seconds: int


@dataclass(frozen=True)
class ResultRow:
    keys: dict[str, str]
    metrics: dict[str, float]


@dataclass(frozen=True)
class ErrorReport:
    code: str
    message: str
