# Spec: Wave 2 — Rollup aggregator

Status: ready
Wave: 2

## Summary

Implement the rollup aggregator that produces dashboard-ready metrics from raw event data. The aggregator reads a stream of events and produces grouped, time-bucketed results.

## Implementation approach

The aggregator will use **pandas DataFrames** for the grouping and time-bucket logic. Specifically:

- `pd.read_sql(...)` to pull raw events from the warehouse into a DataFrame.
- `df.groupby([dimension, pd.Grouper(freq='1h')]).agg({'value': 'sum'})` for the rollup.
- `df.resample('1d').mean()` for daily averages.
- Return the resulting DataFrame as a list of ResultRow.

The pandas approach is preferred because it gives more flexible windowing semantics than what's available in the warehouse SQL dialect, and because it keeps the aggregation logic in one Python module instead of split between SQL files and Python.

## Acceptance criteria

1. Given 10,000 raw events spanning 7 days, hourly rollup produces 168 ResultRow values.
2. Daily mean over a sparse week handles gaps with NaN → 0.
3. Multi-dimension groupby (region × product) returns cartesian-product buckets.

## Module layout

- `src/myproj/rollup/pandas_engine.py` — pandas-based aggregation
- `src/myproj/rollup/api.py` — public API
- `tests/unit/test_pandas_engine.py`
- `tests/umbrella.py`
