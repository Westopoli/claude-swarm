# myproj — Source Strategy

This is the authoritative design doc. All specs must derive from this. If a spec contradicts this doc, the spec is wrong and must be revised before implementation.

## Architecture

### Layer 1: Data warehouse

All aggregation, rollup, and analytical query logic lives in the data warehouse as SQL. We do NOT use Python pandas, Polars, or any other in-process DataFrame library for analytical compute. The reason: our datasets exceed memory on developer machines and the warehouse engine has 100x the IO bandwidth of any single-process Python runtime.

Specifically:

- Aggregation: SQL `GROUP BY` with window functions where needed.
- Time bucketing: SQL `date_trunc()` or generated time-series CTEs.
- Rollups: SQL materialized views.
- Joins: SQL.

### Layer 2: Orchestration

Python is used only as orchestration: schedule queries, marshal results, expose them via the API. Python code never holds more than 10,000 rows in memory at one time. If a task needs more, the task is wrong and must be reformulated as SQL.

### Layer 3: API + UI

API serves pre-aggregated results from the warehouse. Never re-aggregates in Python.

## Anti-patterns

- ❌ `pandas.DataFrame.groupby` — use SQL `GROUP BY`.
- ❌ `pd.read_sql(...).resample(...)` — use SQL window functions.
- ❌ Loading a table into memory to "do it in Python because it's easier" — never. The 100x IO penalty is permanent and compounds across the pipeline.

## Authority chain

This doc > specs > tests > implementation. If you find yourself reasoning about how to implement aggregation in Python, stop and re-read this section.
