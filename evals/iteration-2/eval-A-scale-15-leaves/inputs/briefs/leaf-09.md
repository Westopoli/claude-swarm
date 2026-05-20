---
brief_id: leaf-09
test_file: tests/unit/test_cache_lookup.py
impl_file: src/myproj/cache/lookup.py
spec_lines: 138-152
contract_imports: [CachePolicy, ResultRow]
impl_line_budget: 80
test_assertion_budget: 7
test_owned_by: leaf
wave: 2
---

# Task
Implement cache lookup keyed by query hash. Respect the CachePolicy TTL field. On miss, return None.

# Acceptance
- [ ] miss returns None
- [ ] hit within TTL returns cached ResultRow
- [ ] hit past TTL returns None and evicts
