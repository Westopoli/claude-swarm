---
brief_id: leaf-14
test_file: tests/unit/test_filter_chain.py
impl_file: src/myproj/filters/chain.py
spec_lines: 216-230
contract_imports: [FilterPredicate]
impl_line_budget: 55
test_assertion_budget: 6
test_owned_by: leaf
wave: 2
---

# Task
Chain multiple FilterPredicate objects with AND semantics over a single row.

# Acceptance
- [ ] all predicates pass returns True
- [ ] any predicate fails returns False
- [ ] empty chain returns True
