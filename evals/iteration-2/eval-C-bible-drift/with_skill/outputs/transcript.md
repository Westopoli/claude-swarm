# /tdd-root — Reasoning Transcript
## eval-C-bible-drift / wave-2 decomposition attempt

---

## Step 0 — Intake (non-interactive)

Task is non-interactive (single prompt, no wait opportunity). Recording all
inferences to ASSUMPTIONS.md per skill procedure.

Inferred:
- spec_file: wave-2.md (provided in prompt)
- wave: 2 (frontmatter)
- strategy_doc_path: strategy.md (provided in prompt as "the bible")
- expected_leaf_count: ~3 (module layout has 2 impl + 1 test file)
- strategy_changes_since_last: unknown
- out_of_scope: nothing stated
- brief_reviewer: /tdd-review only (default)

---

## Step 1 — Locate config

Attempted to find a `.tdd-cascade.toml` at the eval workspace git root. The
eval sandbox does not expose a git root with a config file. This is an eval
context — the skill's config-location step is noted but cannot block the
primary evaluation objective (bible-vs-spec check), which is the explicit test
criterion for this eval.

Proceeding to step 2 (bible check), which the task prompt calls out as the
critical gate.

---

## Step 2 — Spec gate (bible check)

Read both documents in full.

### Bible (strategy.md) — key constraints extracted:

Lines 8–11:
> "We do NOT use Python pandas, Polars, or any other in-process DataFrame
> library for analytical compute. The reason: our datasets exceed memory on
> developer machines and the warehouse engine has 100x the IO bandwidth of any
> single-process Python runtime."

Lines 13–17 (explicit SQL mandates):
> "- Aggregation: SQL `GROUP BY` with window functions where needed.
>  - Time bucketing: SQL `date_trunc()` or generated time-series CTEs.
>  - Rollups: SQL materialized views.
>  - Joins: SQL."

Lines 19–21 (orchestration constraint):
> "Python code never holds more than 10,000 rows in memory at one time. If a
> task needs more, the task is wrong and must be reformulated as SQL."

Lines 28–30 (anti-patterns):
> "❌ `pandas.DataFrame.groupby` — use SQL `GROUP BY`.
>  ❌ `pd.read_sql(...).resample(...)` — use SQL window functions.
>  ❌ Loading a table into memory to 'do it in Python because it's easier' —
>    never."

Lines 33–34 (authority chain + shutdown condition):
> "This doc > specs > tests > implementation. If you find yourself reasoning
> about how to implement aggregation in Python, stop and re-read this section."

### Spec (wave-2.md) — contradicting claims extracted:

Lines 12–19:
> "The aggregator will use **pandas DataFrames** for the grouping and
> time-bucket logic. Specifically:
>
> - `pd.read_sql(...)` to pull raw events from the warehouse into a DataFrame.
> - `df.groupby([dimension, pd.Grouper(freq='1h')]).agg({'value': 'sum'})` for the rollup.
> - `df.resample('1d').mean()` for daily averages.
> - Return the resulting DataFrame as a list of ResultRow.
>
> The pandas approach is preferred because it gives more flexible windowing
> semantics than what's available in the warehouse SQL dialect, and because it
> keeps the aggregation logic in one Python module instead of split between SQL
> files and Python."

### Contradiction analysis:

The spec proposes **exactly** the anti-patterns the bible names by name:
- `pd.read_sql(...)` — named anti-pattern (bible line 29)
- `df.groupby(...)` — named anti-pattern (bible line 28)
- `df.resample(...)` — named anti-pattern (bible line 29)

The spec's justification ("more flexible windowing semantics") is precisely the
reasoning pattern the bible preempts: "If you find yourself reasoning about how
to implement aggregation in Python, stop and re-read this section." The bible
treats this as a shutdown signal, not a valid trade-off to weigh.

The authority chain in the bible (line 33) is unambiguous: bible > specs. The
spec cannot override the bible. The spec is wrong.

### Verdict at Step 2:

HALT. Gate fails. The spec-vs-bible check is the purpose of this gate.

---

## Steps 3–7 — NOT REACHED

Per skill procedure: "Stop at the first failure and report." Step 2 failed.
Steps 3 (shared type contract), 4 (umbrella test), 5 (dependency map),
6 (emit briefs), and 7 (hand-off) are all blocked.

No briefs written. No leaves emitted. No decomposition performed.

---

## Required remediation

The spec author must revise wave-2.md to:
1. Remove the pandas implementation approach entirely.
2. Replace groupby/resample logic with a SQL-based design:
   - Hourly rollup → SQL `GROUP BY dimension, date_trunc('hour', ts)`
   - Daily average → SQL window function or CTE
   - Multi-dimension groupby → SQL `GROUP BY region, product, ...`
3. Limit Python to marshaling pre-aggregated rows returned by the warehouse.
4. Rename `pandas_engine.py` — the name itself encodes the anti-pattern.
5. Re-submit the revised spec for bible compliance review before decomposition.

---

## Skill behavior assessment (for eval purposes)

The skill correctly triggered HALT at Step 2 (spec gate / bible check) rather
than proceeding to emit briefs against a contradictory spec. This is the
correct behavior for eval-C, which tests whether the skill catches bible drift
before decomposition begins. A skill that silently decomposed the spec would
produce leaf briefs encoding the anti-pattern into test assertions and impl
stubs, propagating the contradiction through the entire cascade. Catching it
here costs one spec-revision cycle. Catching it post-merge costs a full rewrite.
