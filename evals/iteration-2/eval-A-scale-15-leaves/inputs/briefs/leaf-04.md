---
brief_id: leaf-04
test_file: tests/unit/test_bucket_size.py
impl_file: src/myproj/time/bucket_size.py
spec_lines: 60-72
contract_imports: [BucketSize, TimeRange]
impl_line_budget: 50
test_assertion_budget: 5
test_owned_by: leaf
wave: 1
---

# Task
Given a TimeRange and a BucketSize, produce the list of bucket boundary timestamps covering the range.

# Acceptance
- [ ] range evenly divisible returns N boundaries
- [ ] range non-evenly divisible rounds up to next boundary
- [ ] zero-width range returns single boundary
