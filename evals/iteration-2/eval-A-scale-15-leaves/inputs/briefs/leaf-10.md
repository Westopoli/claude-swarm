---
brief_id: leaf-10
test_file: tests/unit/test_dashboard_view.py
impl_file: src/myproj/dashboard/view.py
spec_lines: 154-168
contract_imports: [DashboardView, AggregatedRow]
impl_line_budget: 60
test_assertion_budget: 6
test_owned_by: leaf
wave: 3
---

# Task
Render a DashboardView to a dict structure suitable for JSON serialization.

# Acceptance
- [ ] name and rows present in output
- [ ] empty rows produces empty array
- [ ] rows preserve order
