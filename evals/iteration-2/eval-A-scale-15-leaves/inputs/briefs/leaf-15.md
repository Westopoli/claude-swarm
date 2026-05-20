---
brief_id: leaf-15
test_file: tests/unit/test_dashboard_export.py
impl_file: src/myproj/dashboard/export.py
spec_lines: 232-246
contract_imports: [DashboardView]
impl_line_budget: 50
test_assertion_budget: 5
test_owned_by: leaf
wave: 3
---

# Task
Export a DashboardView to CSV string. Header row first, then one row per AggregatedRow.

# Acceptance
- [ ] header includes bucket_id and value
- [ ] empty view returns header only
- [ ] values are formatted with .6 precision
