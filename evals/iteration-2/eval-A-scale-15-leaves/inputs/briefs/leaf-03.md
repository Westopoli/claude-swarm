---
brief_id: leaf-03
test_file: tests/unit/test_time_range.py
impl_file: src/myproj/time/time_range.py
spec_lines: 46-58
contract_imports: [TimeRange]
impl_line_budget: 40
test_assertion_budget: 4
test_owned_by: leaf
wave: 1
---

# Task
Implement TimeRange.contains(ts: int) -> bool. Half-open interval [start_ts, end_ts).

# Acceptance
- [ ] start_ts is inclusive
- [ ] end_ts is exclusive
- [ ] ts outside range returns False
