---
brief_id: leaf-07
test_file: tests/unit/test_window_slide.py
impl_file: src/myproj/aggregator/window.py
spec_lines: 106-122
contract_imports: [WindowSpec, AggregatedRow]
impl_line_budget: 90
test_assertion_budget: 8
test_owned_by: leaf
wave: 2
---

# Task
Implement sliding-window aggregation. Given WindowSpec(start, end, bucket_size) and a stream of (ts, value) pairs, produce AggregatedRow per bucket.

# Acceptance
- [ ] empty stream returns empty list
- [ ] single bucket aggregates correctly
- [ ] multi-bucket boundaries respected
- [ ] values outside [start, end) are dropped
