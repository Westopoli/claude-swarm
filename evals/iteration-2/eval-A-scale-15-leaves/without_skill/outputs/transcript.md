# Audit Transcript — 15-Leaf Brief Review (baseline, no skill)

## What Was Checked

### Step 1: Gather all inputs
- Listed all 15 brief files in `.../inputs/briefs/`
- Read the type contract at `.../inputs/src/myproj/types.py`
- Read all 15 briefs via ctx_batch_execute (two batches of 5, then a final batch)

### Step 2: Extract structured fields from each brief
Using Python (ctx_execute), parsed every brief for:
- `brief_id`, `test_file`, `impl_file`
- `contract_imports` (list)
- `impl_line_budget`, `test_assertion_budget`
- `wave`

### Step 3: Three-check audit

**Check A — File ownership overlaps**
Built two dictionaries keyed on `test_file` and `impl_file`. For each brief,
checked whether the file had already been claimed by a prior brief.

Result: 1 overlap found.
- `src/myproj/aggregator/window.py` is claimed by both leaf-07 and leaf-12.
- Both are in wave=2. Their test files differ (test_aggregator_window_sum.py
  vs test_aggregator_window_avg.py), confirming these are meant to be distinct
  slices — but the impl file was not split to match.

**Check B — Symbols in contract_imports vs type contract**
Enumerated all symbols defined in types.py:
  AggregatedRow, WindowSpec, RollupKey, DashboardView, FilterPredicate,
  MetricDef, TimeRange, BucketSize, ResultRow, ErrorReport

For each brief, checked every symbol in `contract_imports` against this set.

Result: 1 missing symbol found.
- leaf-09 imports `CachePolicy`, which is not defined in the type contract.
- `ResultRow` (also imported by leaf-09) is valid.

**Check C — Oversized budgets**
Threshold used: impl_line_budget > 150 OR test_assertion_budget > 15.
These thresholds represent values that would indicate a slice is too large
to be a proper leaf (a single-function unit).

Result: No violations. All budgets are within normal leaf scope.

## Full Brief Summary Table

| ID      | Wave | impl_budget | test_budget | contract_imports              | Issues        |
|---------|------|-------------|-------------|-------------------------------|---------------|
| leaf-01 | 1    | 60          | 6           | FilterPredicate               | none          |
| leaf-02 | 1    | 50          | 5           | MetricDef                     | none          |
| leaf-03 | 1    | 40          | 4           | TimeRange                     | none          |
| leaf-04 | 1    | 50          | 5           | BucketSize, TimeRange         | none          |
| leaf-05 | 1    | 45          | 5           | RollupKey                     | none          |
| leaf-06 | 1    | 70          | 7           | RollupKey, ResultRow          | none          |
| leaf-07 | 2    | 90          | 8           | WindowSpec, AggregatedRow     | IMPL OVERLAP  |
| leaf-08 | 2    | 40          | 4           | AggregatedRow                 | none          |
| leaf-09 | 2    | 80          | 7           | CachePolicy, ResultRow        | MISSING SYMBOL|
| leaf-10 | 3    | 60          | 6           | DashboardView, AggregatedRow  | none          |
| leaf-11 | 1    | 35          | 4           | ErrorReport                   | none          |
| leaf-12 | 2    | 75          | 7           | WindowSpec, AggregatedRow     | IMPL OVERLAP  |
| leaf-13 | 3    | 65          | 6           | ResultRow                     | none          |
| leaf-14 | 2    | 55          | 6           | FilterPredicate               | none          |
| leaf-15 | 3    | 50          | 5           | DashboardView                 | none          |

## Findings Summary

| Check               | Result | Failing Leaves        |
|---------------------|--------|-----------------------|
| File ownership      | FAIL   | leaf-07, leaf-12      |
| Contract symbols    | FAIL   | leaf-09               |
| Budget sizes        | PASS   | —                     |

## Overall Verdict: FAIL
