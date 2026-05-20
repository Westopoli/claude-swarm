---
brief_id: leaf-12
test_file: tests/unit/test_window_tumble.py
impl_file: src/myproj/aggregator/window.py
spec_lines: 184-198
contract_imports: [WindowSpec, AggregatedRow]
impl_line_budget: 75
test_assertion_budget: 7
test_owned_by: leaf
wave: 2
---

# Task
Implement tumbling-window aggregation. Non-overlapping fixed-size buckets aligned to WindowSpec.start.

# Acceptance
- [ ] buckets are non-overlapping
- [ ] alignment respects start
- [ ] final partial bucket is dropped
