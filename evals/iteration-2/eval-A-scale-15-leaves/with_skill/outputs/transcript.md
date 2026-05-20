# TDD-Review Audit Transcript

**Run date**: 2026-05-20
**Briefs directory**: `.../eval-A-scale-15-leaves/inputs/briefs/` (15 briefs: leaf-01 through leaf-15)
**Config**: `.../eval-A-scale-15-leaves/inputs/.tdd-cascade.toml`
**Type contract**: `.../eval-A-scale-15-leaves/inputs/src/myproj/types.py`
**Script status**: `check_invariants.py` not found at `~/.claude/skills/tdd-cascade-shared/scripts/` — manual audit performed per skill fallback instructions.

---

## Step 0: Assumptions Recorded

Non-interactive run. REVIEW_ASSUMPTIONS.md written to briefs dir. Key inferences:
- Multi-wave audit (waves 1, 2, 3 present)
- No known borderline cases
- Config values: max_impl_lines=200, max_test_assertions=20

---

## Step 1: Data Extraction — All 15 Briefs

| leaf_id | test_file | impl_file | wave | impl_budget | test_budget | contract_imports |
|---------|-----------|-----------|------|------------|-------------|-----------------|
| leaf-01 | tests/unit/test_filter_predicate.py | src/myproj/filters/predicate.py | 1 | 60 | 6 | [FilterPredicate] |
| leaf-02 | tests/unit/test_metric_def.py | src/myproj/metrics/metric_def.py | 1 | 50 | 5 | [MetricDef] |
| leaf-03 | tests/unit/test_time_range.py | src/myproj/time/time_range.py | 1 | 40 | 4 | [TimeRange] |
| leaf-04 | tests/unit/test_bucket_size.py | src/myproj/time/bucket_size.py | 1 | 50 | 5 | [BucketSize, TimeRange] |
| leaf-05 | tests/unit/test_rollup_key.py | src/myproj/rollup/key.py | 1 | 45 | 5 | [RollupKey] |
| leaf-06 | tests/unit/test_rollup_groupby.py | src/myproj/rollup/groupby.py | 1 | 70 | 7 | [RollupKey, ResultRow] |
| leaf-07 | tests/unit/test_window_slide.py | **src/myproj/aggregator/window.py** | 2 | 90 | 8 | [WindowSpec, AggregatedRow] |
| leaf-08 | tests/unit/test_aggregator_count.py | src/myproj/aggregator/count.py | 2 | 40 | 4 | [AggregatedRow] |
| leaf-09 | tests/unit/test_cache_lookup.py | src/myproj/cache/lookup.py | 2 | 80 | 7 | [**CachePolicy**, ResultRow] |
| leaf-10 | tests/unit/test_dashboard_view.py | src/myproj/dashboard/view.py | 3 | 60 | 6 | [DashboardView, AggregatedRow] |
| leaf-11 | tests/unit/test_error_report.py | src/myproj/errors/report.py | 1 | 35 | 4 | [ErrorReport] |
| leaf-12 | tests/unit/test_window_tumble.py | **src/myproj/aggregator/window.py** | 2 | 75 | 7 | [WindowSpec, AggregatedRow] |
| leaf-13 | tests/unit/test_result_row_merge.py | src/myproj/rollup/merge.py | 3 | 65 | 6 | [ResultRow] |
| leaf-14 | tests/unit/test_filter_chain.py | src/myproj/filters/chain.py | 2 | 55 | 6 | [FilterPredicate] |
| leaf-15 | tests/unit/test_dashboard_export.py | src/myproj/dashboard/export.py | 3 | 50 | 5 | [DashboardView] |

Bold = flagged values.

---

## Step 2: Invariant 1 — NON-OVERLAP

**Check: duplicate impl_file or test_file across briefs**

Scanning all impl_file values:
- `src/myproj/aggregator/window.py` appears in **leaf-07** AND **leaf-12**. Both in wave 2. Same-wave overlap — definitive failure.

No duplicate test_file values found.

**Check: any impl_file or test_file matches parent_owned globs**

parent_owned globs:
- `src/**/types.py`
- `tests/conftest.py`
- `tests/umbrella*.py`
- `tests/integration/**`

Reviewed all 15 impl_file and test_file paths. None match any parent_owned glob.

**Findings — Invariant 1:**
```
FAIL [leaf-07] non-overlap: impl_file "src/myproj/aggregator/window.py" is also claimed by leaf-12
FAIL [leaf-12] non-overlap: impl_file "src/myproj/aggregator/window.py" is also claimed by leaf-07
```

---

## Step 3: Invariant 2 — NO-DESIGN

**Check: ambiguous verbs in task text**

Reviewed task text for all 15 briefs against the ambiguous_verbs list:
`decide, choose, design, determine, figure out, resolve, as appropriate, use your judgment, pick, select an approach`

- leaf-01: "Implement FilterPredicate evaluation... Return True/False per the op field." — no ambiguous verbs.
- leaf-02: "Validate a MetricDef. Aggregation must be one of sum/avg/min/max/count. Name must be non-empty." — no ambiguous verbs.
- leaf-03: "Implement TimeRange.contains(ts: int) -> bool. Half-open interval [start_ts, end_ts)." — no ambiguous verbs.
- leaf-04: "Given a TimeRange and a BucketSize, produce the list of bucket boundary timestamps covering the range." — no ambiguous verbs.
- leaf-05: "Implement RollupKey serialization to canonical string form 'dimension=value'." — no ambiguous verbs.
- leaf-06: "Group a list of ResultRow by the listed dimension. Return dict[RollupKey, list[ResultRow]]." — no ambiguous verbs.
- leaf-07: "Implement sliding-window aggregation. Given WindowSpec(start, end, bucket_size) and a stream of (ts, value) pairs, produce AggregatedRow per bucket." — no ambiguous verbs.
- leaf-08: "Implement count() aggregation over bucketed inputs. Return AggregatedRow with value = len(bucket)." — no ambiguous verbs.
- leaf-09: "Implement cache lookup keyed by query hash. Respect the CachePolicy TTL field. On miss, return None." — no ambiguous verbs in verb list, but see contract check below.
- leaf-10: "Render a DashboardView to a dict structure suitable for JSON serialization." — no ambiguous verbs.
- leaf-11: "Format an ErrorReport into a single-line log string '[code] message'." — no ambiguous verbs.
- leaf-12: "Implement tumbling-window aggregation. Non-overlapping fixed-size buckets aligned to WindowSpec.start." — no ambiguous verbs.
- leaf-13: "Merge two ResultRow values with identical keys. Sum the metric values. Fail on key mismatch." — no ambiguous verbs.
- leaf-14: "Chain multiple FilterPredicate objects with AND semantics over a single row." — no ambiguous verbs.
- leaf-15: "Export a DashboardView to CSV string. Header row first, then one row per AggregatedRow." — no ambiguous verbs.

No ambiguous verb violations found.

**Check: contract_imports references symbols not in locked type contract**

Locked contract symbols (from `src/myproj/types.py`):
`AggregatedRow, WindowSpec, RollupKey, DashboardView, FilterPredicate, MetricDef, TimeRange, BucketSize, ResultRow, ErrorReport`

Reviewing each brief's contract_imports:
- leaf-01: [FilterPredicate] — OK
- leaf-02: [MetricDef] — OK
- leaf-03: [TimeRange] — OK
- leaf-04: [BucketSize, TimeRange] — OK
- leaf-05: [RollupKey] — OK
- leaf-06: [RollupKey, ResultRow] — OK
- leaf-07: [WindowSpec, AggregatedRow] — OK
- leaf-08: [AggregatedRow] — OK
- leaf-09: [**CachePolicy**, ResultRow] — **FAIL**: `CachePolicy` is NOT defined in `src/myproj/types.py`
- leaf-10: [DashboardView, AggregatedRow] — OK
- leaf-11: [ErrorReport] — OK
- leaf-12: [WindowSpec, AggregatedRow] — OK
- leaf-13: [ResultRow] — OK
- leaf-14: [FilterPredicate] — OK
- leaf-15: [DashboardView] — OK

**Findings — Invariant 2:**
```
FAIL [leaf-09] no-design: contract_imports references "CachePolicy" which is NOT in the locked type contract (src/myproj/types.py)
```

---

## Step 4: Invariant 3 — SIZING

**Check: impl_line_budget > max_impl_lines (200)**

All values: 60, 50, 40, 50, 45, 70, 90, 40, 80, 60, 35, 75, 65, 55, 50
Maximum observed: 90 (leaf-07). All under 200. No violations.

**Check: test_assertion_budget > max_test_assertions (20)**

All values: 6, 5, 4, 5, 5, 7, 8, 4, 7, 6, 4, 7, 6, 6, 5
Maximum observed: 8 (leaf-07). All under 20. No violations.

**Findings — Invariant 3:**
```
PASS — all sizing budgets within limits
```

---

## Summary of All Findings

```
FAIL [leaf-07] non-overlap: impl_file "src/myproj/aggregator/window.py" also claimed by leaf-12
FAIL [leaf-12] non-overlap: impl_file "src/myproj/aggregator/window.py" also claimed by leaf-07
FAIL [leaf-09] no-design: contract_imports references "CachePolicy" — symbol absent from src/myproj/types.py
```

Total briefs: 15
Passing briefs: 12
Failing briefs: 3 (leaf-07, leaf-09, leaf-12)
