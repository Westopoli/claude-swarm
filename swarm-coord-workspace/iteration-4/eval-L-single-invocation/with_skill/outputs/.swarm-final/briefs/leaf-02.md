---
leaf_id: leaf-02
spec_file: specs/url_utils.md
spec_lines: 21-30
test_file: tests/test_is_safe_url.py
impl_file: src/url_utils/is_safe_url.py
contract_imports:
  - ParsedUrl
do_not_edit:
  - src/url_utils/parse_url.py
  - tests/test_parse_url.py
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

Implement `is_safe_url(url: str, allowed_hosts: list[str]) -> bool` at `src/url_utils/is_safe_url.py`, per spec_lines 21-30 of `specs/url_utils.md`. The implementation must NOT import from `url_utils.parse_url` (that is a sibling leaf — cross-leaf imports are forbidden in this wave). Use `urllib.parse.urlsplit` directly to extract scheme and host. At module top level, after defining the concrete `is_safe_url` function, assign it to `url_utils.types.is_safe_url` so callers that do `from url_utils.types import is_safe_url` after this module is imported will receive the concrete function (the parent `conftest.py` imports this module at test-collection time to apply this rebinding). Behaviour per spec: return `True` iff the URL has a non-empty scheme and non-empty host (parses validly) AND the lowercased parsed host matches some entry in `allowed_hosts` case-insensitively. Return `False` for any input that has no scheme separator (`://`) producing both non-empty scheme and non-empty host — do not raise. Use only the Python standard library. Do not create any file outside impl_file. Do not modify `tests/test_is_safe_url.py`.

## Acceptance

Run `pytest tests/test_is_safe_url.py -x` for this test_file. Confirm RED before implementing. Implement in impl_file only. Confirm GREEN. Stage final files to `.swarm/pending/leaf-02/` mirroring paths from project root (`src/url_utils/is_safe_url.py` → `.swarm/pending/leaf-02/src/url_utils/is_safe_url.py`; the unchanged test file → `.swarm/pending/leaf-02/tests/test_is_safe_url.py`). Stop. Do not copy to real destinations.

## Escalation triggers

Stop and report to the parent if:
- The test imports a type not in contract_imports.
- The impl would need to create a file other than impl_file.
- The impl would need to edit a file in do_not_edit.
- Impl approaches impl_line_budget with assertions still failing.
