---
brief_id: leaf-08
test_file: tests/unit/test_aggregator_count.py
impl_file: src/myproj/aggregator/count.py
spec_lines: 124-136
contract_imports: [AggregatedRow]
impl_line_budget: 40
test_assertion_budget: 4
test_owned_by: leaf
wave: 2
---

# Task
Implement count() aggregation over bucketed inputs. Return AggregatedRow with value = len(bucket).

# Acceptance
- [ ] empty bucket returns value=0
- [ ] single-item bucket returns value=1
- [ ] N-item bucket returns value=N
