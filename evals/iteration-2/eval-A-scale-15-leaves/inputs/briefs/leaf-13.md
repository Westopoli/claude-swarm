---
brief_id: leaf-13
test_file: tests/unit/test_result_row_merge.py
impl_file: src/myproj/rollup/merge.py
spec_lines: 200-214
contract_imports: [ResultRow]
impl_line_budget: 65
test_assertion_budget: 6
test_owned_by: leaf
wave: 3
---

# Task
Merge two ResultRow values with identical keys. Sum the metric values. Fail on key mismatch.

# Acceptance
- [ ] identical-key rows sum correctly
- [ ] mismatched keys raise ValueError
- [ ] disjoint metric names union
