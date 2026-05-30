---
leaf_id: leaf-01
spec_file: specs/url_utils.md
spec_lines: 9-19
test_file: tests/test_parse_url.py
impl_file: src/url_utils/parse_url.py
contract_imports:
  - url_utils.types.ParsedUrl
do_not_edit:
  - src/url_utils/types.py
  - src/url_utils/is_safe_url.py
  - tests/test_is_safe_url.py
  - tests/umbrella.py
  - tests/conftest.py
  - tests/integration/**
  - src/**/types.py
impl_line_budget: 60
test_assertion_budget: 12
---

## Task

Implement `parse_url(url: str) -> ParsedUrl` per spec_lines 9-19 of `specs/url_utils.md`. Place the implementation in `src/url_utils/parse_url.py` as a top-level function named `parse_url`. The function lowercases the scheme, lowercases the host, preserves path case, returns path `"/"` when the URL has no path component, and raises `ValueError` when the input has no scheme. Import `ParsedUrl` from `url_utils.types`. Write tests in `tests/test_parse_url.py` that import `parse_url` from `url_utils.parse_url` (not from `url_utils.types`); each example in spec_lines 17-19 maps to one assertion.

Then write a contract-proposal at `.swarm/proposals/leaf-01.md` requesting the parent edit `src/url_utils/types.py` to replace the `parse_url` stub body with a re-export that delegates to `url_utils.parse_url.parse_url`, so the umbrella's existing `from url_utils.types import parse_url` points at the implementation. The parent applies the contract-proposal after admission.

## Acceptance

Run `python3 -m pytest tests/test_parse_url.py -x` for this test_file. Confirm RED before impl. Implement in impl_file only. Confirm GREEN. Write your final `test_file` and `impl_file` to `.swarm/pending/leaf-01/` mirroring their paths from the project root (e.g. `src/url_utils/parse_url.py` → `.swarm/pending/leaf-01/src/url_utils/parse_url.py`). Stop. Do not copy files to their real destinations — `/swarm-post-review` does that after gating.

## Escalation triggers

Stop and report to the parent if:
- A type the test imports is not in contract_imports.
- The impl would need to create a new file outside `src/url_utils/parse_url.py` or `tests/test_parse_url.py`.
- The impl would need to edit a file in do_not_edit.
- Impl approaches impl_line_budget with assertions still failing.
