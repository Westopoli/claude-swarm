---
leaf_id: leaf-01
spec_file: specs/url_utils.md
spec_lines: 9-19
test_file: tests/test_parse_url.py
impl_file: src/url_utils/parse_url.py
contract_imports:
  - ParsedUrl
do_not_edit:
  - src/url_utils/is_safe_url.py
  - tests/test_is_safe_url.py
  - src/url_utils/types.py
  - tests/conftest.py
  - tests/umbrella.py
  - conftest.py
impl_line_budget: 60
test_assertion_budget: 10
test_owned_by: parent
wave: 1
---

## Task

Implement `parse_url(url: str) -> ParsedUrl` at `src/url_utils/parse_url.py`, per spec_lines 9-19 of `specs/url_utils.md`. The implementation must import `ParsedUrl` from `url_utils.types`. At module top level, after defining the concrete `parse_url` function, assign it to `url_utils.types.parse_url` so callers that do `from url_utils.types import parse_url` after this module is imported will receive the concrete function (the parent `conftest.py` imports this module at test-collection time to apply this rebinding). Behaviour per spec: lowercase the scheme; lowercase the host; preserve the path component case verbatim; return `"/"` as the path when the URL contains no path; raise `ValueError` when the input string has no scheme separator (`://`) producing a non-empty scheme and non-empty host. Use only the Python standard library (`urllib.parse`). Do not create any file outside impl_file. Do not modify `tests/test_parse_url.py`.

## Acceptance

Run `pytest tests/test_parse_url.py -x` for this test_file. Confirm RED before implementing. Implement in impl_file only. Confirm GREEN. Stage final files to `.swarm/pending/leaf-01/` mirroring paths from project root (`src/url_utils/parse_url.py` → `.swarm/pending/leaf-01/src/url_utils/parse_url.py`; the unchanged test file → `.swarm/pending/leaf-01/tests/test_parse_url.py`). Stop. Do not copy to real destinations.

## Escalation triggers

Stop and report to the parent if:
- The test imports a type not in contract_imports.
- The impl would need to create a file other than impl_file.
- The impl would need to edit a file in do_not_edit.
- Impl approaches impl_line_budget with assertions still failing.
