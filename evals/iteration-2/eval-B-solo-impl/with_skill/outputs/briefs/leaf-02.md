---
leaf_id: leaf-02
spec_file: specs/feature-aggregator.md
spec_lines: 1-31
test_file: tests/unit/test_sliding_aggregator.py
impl_file: src/myproj/aggregator/sliding.py
contract_imports:
  - myproj.types.AggregatedRow
  - myproj.types.WindowSpec
do_not_edit:
  - src/**/types.py
  - tests/conftest.py
  - tests/umbrella*.py
  - tests/integration/**
  - src/myproj/aggregator/buckets.py
  - tests/unit/test_buckets.py
impl_line_budget: 120
test_assertion_budget: 15
wave: 1
---

## Task

Implement `src/myproj/aggregator/sliding.py`. This module must expose one public function:

```
def aggregate(
    spec: WindowSpec,
    stream: Iterable[tuple[int, float]],
    mode: str,
    overlap: float = 0.0,
) -> list[AggregatedRow]:
    ...
```

`stream` is an iterable of `(timestamp, value)` pairs. `mode` must accept exactly the strings `"sum"`, `"avg"`, and `"count"`. This module calls `compute_bucket_boundaries` from `src/myproj/aggregator/buckets.py` (leaf-01's impl file — ensure leaf-01 is green before this leaf runs).

Per spec lines 9-14 (acceptance criteria 1-5):

1. (Criterion 1) `aggregate(WindowSpec(0, 100, 10), stream_of_30_events, "sum")` where events are evenly distributed must return exactly 10 `AggregatedRow` values.
2. (Criterion 2) Events with `timestamp < spec.start` or `timestamp >= spec.end` must be silently dropped — they must not appear in any returned `AggregatedRow`.
3. (Criterion 3) For `mode="avg"`, a bucket that received zero events must produce `AggregatedRow(bucket_id=<bucket_label>, value=0.0)` — not `NaN`, not a missing entry.
4. (Criterion 4) For `mode="count"`, `AggregatedRow.value` must equal the integer count of events whose timestamp falls within that bucket's `[bucket_start, bucket_end)` range. The value field is typed `float` in the contract; cast the count: `float(n)`.
5. (Criterion 5) With `overlap=0.5`, `aggregate` must produce `2N-1` `AggregatedRow` values for a stream spanning exactly `N` bucket_sizes. The `overlap` parameter is forwarded directly to `compute_bucket_boundaries`.

Each returned `AggregatedRow` must have a `bucket_id` string that matches the label produced by `compute_bucket_boundaries` for that bucket (e.g., `"bucket_0"`, `"bucket_1"`, …). Do not invent an alternative label scheme — use whatever `buckets.py` returns.

`mode` values other than `"sum"`, `"avg"`, `"count"` must raise `ValueError`. The spec does not prescribe the error message; use any descriptive string.

The function is single-threaded (spec out-of-scope, line 18). No persistence (spec out-of-scope, line 17). No cache invalidation (spec out-of-scope, line 19).

## Acceptance

Run `pytest tests/unit/test_sliding_aggregator.py` for this test_file. Confirm RED. Implement `src/myproj/aggregator/sliding.py` only. Confirm GREEN. Commit the two files. Stop.

**Prerequisite**: leaf-01 (`src/myproj/aggregator/buckets.py`) must be green before this leaf begins. If `buckets.py` does not exist or its tests fail, stop and report to the parent.

## Escalation triggers

Stop and report to the parent if:

- A type the test imports is not in contract_imports.
- The impl would need to create a new file.
- The impl would need to edit a file in do_not_edit.
- `buckets.py` does not exist when your test attempts to import it.
- Two sibling assertions seem to require contradictory behavior.
- Impl approaches impl_line_budget (120 lines) with assertions still failing.
- The bucket_id label format produced by buckets.py differs from what your test expects — escalate, do not adapt silently.

## Assumption log

If at any point during your run you had to infer something the brief did not specify (a default value, an error code, a representation choice, anything), write it to `briefs/leaf-02.ASSUMPTIONS.md` before you commit. Format:

```markdown
## Assumptions made during leaf-02

- **<thing>**: <inferred value> — source: <which spec line / contract symbol / file you looked at, or "no source — pure guess">
```

Do not bury inferences inside impl comments. The parent runs an assumption-sweep across all leaves before any merge — that sweep only sees the .ASSUMPTIONS.md files. An undocumented inference cannot be swept.
