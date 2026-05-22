---
leaf_id: leaf-03
spec_file: specs/cache.md
spec_lines: 10-25
test_file: tests/test_cache_ttl.py
impl_file: src/cache.py
contract_imports:
  - src.cache.Cache
do_not_edit:
  - tests/umbrella.py
impl_line_budget: 50
test_assertion_budget: 5
---

## Task

Add TTL support to Cache.get() and Cache.set(). Reference spec lines 10-25.

## Acceptance

Run `pytest tests/test_cache_ttl.py -v` for this test_file. Confirm RED. Implement in src/cache.py only. Confirm GREEN. Write your final files to .swarm/pending/leaf-03/. Stop.

## Escalation triggers

Stop and report to the parent if the impl would need to edit a file in do_not_edit.
