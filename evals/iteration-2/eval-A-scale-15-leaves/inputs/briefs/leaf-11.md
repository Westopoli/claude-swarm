---
brief_id: leaf-11
test_file: tests/unit/test_error_report.py
impl_file: src/myproj/errors/report.py
spec_lines: 170-182
contract_imports: [ErrorReport]
impl_line_budget: 35
test_assertion_budget: 4
test_owned_by: leaf
wave: 1
---

# Task
Format an ErrorReport into a single-line log string "[code] message".

# Acceptance
- [ ] basic format
- [ ] code with brackets is escaped
- [ ] empty message renders "[code] "
