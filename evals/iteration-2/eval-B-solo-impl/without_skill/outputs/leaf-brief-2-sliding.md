# Leaf Brief 2 — Sliding Aggregation Logic

## Assignment
- Test file: `tests/unit/test_sliding_aggregator.py`
- Impl file: `src/myproj/aggregator/sliding.py`

## Spec slice
Acceptance criteria 2, 3, 4:
- AC2: Events with timestamp < start or >= end are dropped silently
- AC3: Average aggregation over empty bucket returns AggregatedRow(value=0.0)
- AC4: Count aggregation matches len of events in bucket

## Behavior to implement
`aggregate(stream: Iterable[tuple[int, float]], spec: WindowSpec, mode: str, buckets: list[tuple[int, int]]) -> list[AggregatedRow]`
- Accepts stream of (timestamp, value) pairs
- Drops events outside [spec.start, spec.end)
- For each bucket (bucket_start, bucket_end), collects events where bucket_start <= timestamp < bucket_end
- mode="sum": sums values in bucket
- mode="average": averages values; returns 0.0 for empty bucket
- mode="count": returns float(len(events in bucket))
- Returns one AggregatedRow per bucket, bucket_id = f"{bucket_start}-{bucket_end}"

## Imports allowed
- `from myproj.types import AggregatedRow, WindowSpec`
- `from myproj.aggregator.buckets import compute_buckets`
- Standard library only (no third-party packages)

## Constraints
- Do NOT edit types.py or buckets.py
- Do NOT create any files other than your two assigned files
- bucket boundary logic lives in buckets.py — import it, don't re-implement it
