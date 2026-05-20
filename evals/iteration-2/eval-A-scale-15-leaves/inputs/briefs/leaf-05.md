---
brief_id: leaf-05
test_file: tests/unit/test_rollup_key.py
impl_file: src/myproj/rollup/key.py
spec_lines: 74-86
contract_imports: [RollupKey]
impl_line_budget: 45
test_assertion_budget: 5
test_owned_by: leaf
wave: 1
---

# Task
Implement RollupKey serialization to canonical string form "dimension=value".

# Acceptance
- [ ] basic key serializes correctly
- [ ] empty dimension raises ValueError
- [ ] value containing "=" is escaped
