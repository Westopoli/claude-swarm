# Leaf Brief 1 — Bucket Boundary Computation

## Assignment
- Test file: `tests/unit/test_buckets.py`
- Impl file: `src/myproj/aggregator/buckets.py`

## Spec slice
Acceptance criteria 1 and 5:
- AC1: WindowSpec(start=0, end=100, bucket_size=10) with 30 evenly distributed events → 10 buckets
- AC5: Sliding overlap factor of 0.5 produces 2N-1 buckets for a stream spanning N bucket_sizes

## Behavior to implement
`compute_buckets(spec: WindowSpec, overlap: float = 0.0) -> list[tuple[int, int]]`
- Returns a list of (bucket_start, bucket_end) tuples covering [spec.start, spec.end)
- When overlap=0.0, non-overlapping: bucket count = (end - start) / bucket_size
- When overlap=0.5, stride = bucket_size * (1 - overlap), produces 2N-1 buckets for N bucket_sizes

## Imports allowed
- `from myproj.types import WindowSpec`

## Constraints
- Do NOT edit types.py
- Do NOT create any files other than your two assigned files
- Do NOT implement aggregation logic — only bucket boundary math
