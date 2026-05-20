---
brief_id: leaf-06
test_file: tests/unit/test_rollup_groupby.py
impl_file: src/myproj/rollup/groupby.py
spec_lines: 88-104
contract_imports: [RollupKey, ResultRow]
impl_line_budget: 70
test_assertion_budget: 7
test_owned_by: leaf
wave: 1
---

# Task
Group a list of ResultRow by the listed dimension. Return dict[RollupKey, list[ResultRow]].

# Acceptance
- [ ] single-dimension groupby returns correct buckets
- [ ] missing dimension raises KeyError
- [ ] empty input returns empty dict
