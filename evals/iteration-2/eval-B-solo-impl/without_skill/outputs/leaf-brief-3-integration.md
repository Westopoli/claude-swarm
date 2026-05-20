# Leaf Brief 3 — Pipeline Integration Test

## Assignment
- Test file: `tests/integration/test_aggregator_pipeline.py`
- Impl file: None (integration test only; wires existing modules)

## Spec slice
Acceptance criterion 1 (end-to-end):
- AC1: WindowSpec(start=0, end=100, bucket_size=10), 30 events evenly distributed, mode="sum" → 10 AggregatedRow values

## Behavior to verify
- Import `aggregate` from `myproj.aggregator.sliding`
- Import `compute_buckets` from `myproj.aggregator.buckets`
- Construct 30 events: timestamps 0..99 evenly spread, values arbitrary (e.g., 1.0 each)
- Call aggregate with mode="sum", non-overlapping buckets (overlap=0.0)
- Assert len(result) == 10
- Assert all results are AggregatedRow instances
- Assert each bucket has value == 3.0 (30 events / 10 buckets)

## Imports allowed
- `from myproj.types import AggregatedRow, WindowSpec`
- `from myproj.aggregator.sliding import aggregate`
- `from myproj.aggregator.buckets import compute_buckets`

## Constraints
- Do NOT edit types.py, buckets.py, or sliding.py
- Do NOT create impl files — this leaf is test-only
- This test is integration: it may only pass after Leaf 1 and Leaf 2 are green
