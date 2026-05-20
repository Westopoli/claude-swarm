---
leaf_id: leaf-01
spec_file: specs/feature-aggregator.md
spec_lines: 1-31
test_file: tests/unit/test_buckets.py
impl_file: src/myproj/aggregator/buckets.py
contract_imports:
  - myproj.types.WindowSpec
do_not_edit:
  - src/**/types.py
  - tests/conftest.py
  - tests/umbrella*.py
  - tests/integration/**
  - src/myproj/aggregator/sliding.py
  - tests/unit/test_sliding_aggregator.py
impl_line_budget: 80
test_assertion_budget: 10
wave: 1
---

## Task

Implement `src/myproj/aggregator/buckets.py`. This module must expose one public function:

```
def compute_bucket_boundaries(spec: WindowSpec) -> list[tuple[int, int]]:
    ...
```

Per spec lines 8-14 (WindowSpec fields: start, end, bucket_size), `compute_bucket_boundaries` must return a list of `(bucket_start, bucket_end)` integer tuples covering `[spec.start, spec.end)` in non-overlapping increments of `spec.bucket_size`. Per spec line 9 (acceptance criterion 1), a `WindowSpec(start=0, end=100, bucket_size=10)` must produce exactly 10 buckets. Per spec line 10 (criterion 2), timestamps at or after `spec.end` are outside any bucket boundary; timestamps before `spec.start` are also outside — buckets must not extend beyond `[spec.start, spec.end)`. Per spec line 13 (criterion 5), when called with an overlap factor of 0.5, the function must instead produce `2N-1` buckets for a stream spanning N bucket_sizes; expose this as an optional parameter `overlap: float = 0.0` where `0.0` means no overlap and `0.5` means 50% step (step = `bucket_size * (1 - overlap)`). If overlap produces a fractional step, round down to the nearest integer (minimum step of 1).

The `bucket_id` string label for each bucket is not prescribed by the spec; use `"bucket_N"` where N is the zero-based index. Write this convention to `briefs/leaf-01.ASSUMPTIONS.md` before committing.

## Acceptance

Run `pytest tests/unit/test_buckets.py` for this test_file. Confirm RED. Implement `src/myproj/aggregator/buckets.py` only. Confirm GREEN. Commit the two files. Stop.

## Escalation triggers

Stop and report to the parent if:

- A type the test imports is not in contract_imports.
- The impl would need to create a new file.
- The impl would need to edit a file in do_not_edit.
- Two sibling assertions seem to require contradictory behavior.
- Impl approaches impl_line_budget (80 lines) with assertions still failing.
- `overlap` semantics are ambiguous for a given test case — do not guess; escalate.

## Assumption log

If at any point during your run you had to infer something the brief did not specify (a default value, an error code, a representation choice, anything), write it to `briefs/leaf-01.ASSUMPTIONS.md` before you commit. Format:

```markdown
## Assumptions made during leaf-01

- **<thing>**: <inferred value> — source: <which spec line / contract symbol / file you looked at, or "no source — pure guess">
```

Do not bury inferences inside impl comments. The parent runs an assumption-sweep across all leaves before any merge — that sweep only sees the .ASSUMPTIONS.md files. An undocumented inference cannot be swept.
