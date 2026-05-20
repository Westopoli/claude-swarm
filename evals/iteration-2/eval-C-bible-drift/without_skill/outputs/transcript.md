# Reasoning Transcript — Wave-2 Decomposition Attempt

## Step 1: Read both input files

Read `strategy.md` and `wave-2.md` in parallel before doing any planning.

## Step 2: Cross-check spec against strategy doc

The strategy doc opens with an explicit authority statement:
> "This is the authoritative design doc. All specs must derive from this. If a spec
> contradicts this doc, the spec is wrong and must be revised before implementation."

And establishes the authority chain:
> "This doc > specs > tests > implementation."

I then checked wave-2.md's implementation approach against the strategy constraints.

## Step 3: Identify contradiction

Strategy doc prohibits:
- Any in-process DataFrame library (pandas, Polars, etc.) for analytical compute
- `pandas.DataFrame.groupby` — must use SQL `GROUP BY`
- `pd.read_sql(...).resample(...)` — must use SQL window functions
- Loading tables into memory to aggregate in Python

Wave-2.md mandates:
- `pd.read_sql(...)` to pull raw events into a DataFrame
- `df.groupby([dimension, pd.Grouper(freq='1h')]).agg(...)` for rollup
- `df.resample('1d').mean()` for daily averages
- A module named `pandas_engine.py`

This is a direct, point-for-point contradiction of every anti-pattern the strategy doc
explicitly calls out. The spec even mirrors the exact code patterns listed as forbidden
(`pd.read_sql`, `.resample`).

## Step 4: Decision

Because the strategy doc is the top of the authority chain and explicitly states that
conflicting specs are wrong and must be revised, I halted decomposition.

Proceeding would mean:
1. Writing tests that encode a forbidden architectural pattern
2. Writing implementation that violates the strategy's core constraint
3. Creating a `pandas_engine.py` module that the strategy says should not exist

None of these are recoverable by later refactoring — they encode the wrong architecture
into the test suite itself.

## Step 5: What would correct resolution look like?

Wave-2.md needs to be rewritten so the rollup logic lives in:
- A SQL materialized view (for the rollup aggregation)
- SQL `date_trunc()` or a generated time-series CTE (for time bucketing)
- A Python orchestration layer that only schedules/marshals results (no groupby/resample)

The module layout would change from `pandas_engine.py` to something like
`sql_rollup_view.sql` + a thin Python `api.py` that queries the pre-aggregated view.

Only after the spec is revised to match the strategy doc should decomposition begin.

## Outcome

HALT. Contradiction detected. No leaf briefs produced. Spec must be revised first.
