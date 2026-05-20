---
brief_id: leaf-02
test_file: tests/unit/test_metric_def.py
impl_file: src/myproj/metrics/metric_def.py
spec_lines: 30-44
contract_imports: [MetricDef]
impl_line_budget: 50
test_assertion_budget: 5
test_owned_by: leaf
wave: 1
---

# Task
Validate a MetricDef. Aggregation must be one of sum/avg/min/max/count. Name must be non-empty.

# Acceptance
- [ ] valid MetricDef passes
- [ ] empty name raises ValueError
- [ ] unknown aggregation raises ValueError
