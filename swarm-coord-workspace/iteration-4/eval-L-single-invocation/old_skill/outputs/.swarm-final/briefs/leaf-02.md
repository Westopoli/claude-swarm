---
leaf_id: leaf-02
spec_file: specs/url_utils.md
spec_lines: 21-30
test_file: tests/test_is_safe_url.py
impl_file: src/url_utils/is_safe_url.py
contract_imports:
  - url_utils.types.ParsedUrl
do_not_edit:
  - src/url_utils/types.py
  - src/url_utils/parse_url.py
  - tests/test_parse_url.py
  - tests/umbrella.py
  - tests/conftest.py
  - tests/integration/**
  - src/**/types.py
impl_line_budget: 40
test_assertion_budget: 12
---

## Task

Implement `is_safe_url(url: str, allowed_hosts: list[str]) -> bool` per spec_lines 21-30 of `specs/url_utils.md`. Place the implementation in `src/url_utils/is_safe_url.py` as a top-level function named `is_safe_url`. The function returns `True` iff `parse_url(url)` does not raise AND the parsed `host` is in `allowed_hosts` (case-insensitive match on host). When `parse_url(url)` raises `ValueError`, the function returns `False` (does not re-raise). Import `parse_url` from `url_utils.parse_url` (the sibling impl module written by leaf-01); do not import `parse_url` from `url_utils.types`. Write tests in `tests/test_is_safe_url.py` that import `is_safe_url` from `url_utils.is_safe_url`; each example in spec_lines 28-30 maps to one assertion.

Then write a contract-proposal at `.swarm/proposals/leaf-02.md` requesting the parent edit `src/url_utils/types.py` to replace the `is_safe_url` stub body with a re-export that delegates to `url_utils.is_safe_url.is_safe_url`, so the umbrella's existing `from url_utils.types import is_safe_url` points at the implementation. The parent applies the contract-proposal after admission.

## Sibling-dependency note

This leaf imports `parse_url` from `url_utils.parse_url`, which is the impl module owned by leaf-01. At test-run time inside `.swarm/pending/leaf-02/`, leaf-01's impl may not yet be staged. Stage your impl assuming leaf-01's impl exists at `src/url_utils/parse_url.py` by the time `/swarm-post-review` runs admission for this leaf. If running the test in isolation fails because leaf-01 has not been admitted yet, that is acceptable — record it in `.swarm/briefs/leaf-02.ASSUMPTIONS.md` and the post-review G2 step will re-run after both leaves are staged.

## Acceptance

Run `python3 -m pytest tests/test_is_safe_url.py -x` for this test_file. Confirm RED before impl. Implement in impl_file only. Confirm GREEN (or document the sibling-dependency block above). Write your final `test_file` and `impl_file` to `.swarm/pending/leaf-02/` mirroring their paths from the project root. Stop. Do not copy files to their real destinations — `/swarm-post-review` does that after gating.

## Escalation triggers

Stop and report to the parent if:
- A type the test imports is not in contract_imports.
- The impl would need to create a new file outside `src/url_utils/is_safe_url.py` or `tests/test_is_safe_url.py`.
- The impl would need to edit a file in do_not_edit.
- Impl approaches impl_line_budget with assertions still failing.
