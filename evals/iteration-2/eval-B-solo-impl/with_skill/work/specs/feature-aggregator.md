# Feature: Sliding-window aggregator

Status: ready
Wave: 1

## Summary

Implement a sliding-window aggregator that consumes a stream of (timestamp, value) pairs and emits one AggregatedRow per bucket. Three aggregation modes required: sum, average, count.

## Acceptance criteria

1. Given WindowSpec(start=0, end=100, bucket_size=10) and stream of 30 events evenly distributed, sum-aggregation produces 10 AggregatedRow values.
2. Values with timestamp < start or >= end are dropped silently.
3. Average aggregation over empty bucket returns AggregatedRow(value=0.0).
4. Count aggregation matches len of events in bucket.
5. Sliding overlap factor of 0.5 produces 2N-1 buckets for a stream spanning N bucket_sizes.

## Out of scope

- Persistence — caller passes stream as a Python iterable.
- Concurrency — single-threaded only.
- Cache invalidation — separate spec.

## Module layout

- `src/myproj/aggregator/sliding.py` — main aggregation logic
- `src/myproj/aggregator/buckets.py` — bucket boundary computation
- `tests/unit/test_sliding_aggregator.py` — unit coverage
- `tests/integration/test_aggregator_pipeline.py` — pipeline integration
- `tests/umbrella.py` — acceptance criteria 1-5 as assertions
