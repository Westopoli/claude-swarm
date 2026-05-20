---
brief_id: leaf-01
test_file: tests/unit/test_filter_predicate.py
impl_file: src/myproj/filters/predicate.py
spec_lines: 12-28
contract_imports: [FilterPredicate]
impl_line_budget: 60
test_assertion_budget: 6
test_owned_by: leaf
wave: 1
---

# Task
Implement FilterPredicate evaluation against a single row dict. Return True/False per the op field.

# Acceptance
- [ ] eq, ne, gt, lt, in all return correct values for representative inputs
- [ ] missing field raises KeyError
