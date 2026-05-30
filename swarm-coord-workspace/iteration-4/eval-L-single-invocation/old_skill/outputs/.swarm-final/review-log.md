# /swarm-review — invariant audit

Audit run on `.swarm/briefs/` (manual replay of `check_invariants.py` logic; bash subprocess execution was sandbox-blocked during this eval, so the audit was replayed by inspection of the script source).

## Per-brief verdict

- leaf-01: PASS
- leaf-02: PASS

## Checks replayed

1. **Schema** — all required fields (`leaf_id`, `spec_file`, `spec_lines`, `test_file`, `impl_file`, `contract_imports`, `do_not_edit`, `impl_line_budget`, `test_assertion_budget`) present on both briefs; `leaf_id` unique.
2. **Non-overlap** — both impl paths (`src/url_utils/parse_url.py`, `src/url_utils/is_safe_url.py`) and both test paths (`tests/test_parse_url.py`, `tests/test_is_safe_url.py`) miss every parent-owned glob in `.claude-swarm.toml`; each brief's `do_not_edit` lists the sibling's impl + test files.
3. **No-design** — `spec_lines` ranges `9-19` and `21-30` match the concrete `int-int` regex; `contract_imports` reference `ParsedUrl`, which exists in the locked contract `src/url_utils/types.py`; task prose contains none of the configured ambiguous verbs (`decide`, `choose`, `design`, `determine`, `figure out`, `resolve`, `as appropriate`, `use your judgment`, `pick`, `select an approach`).
4. **Sizing** — `impl_line_budget` 60 and 40 are within max 200; `test_assertion_budget` 12 each within max 20.

## Summary

`--- 2/2 briefs PASS, 0 findings ---`

Verdict: **all PASS**. Parent may spawn leaves.
