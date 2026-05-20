# Leaf Brief — Canonical Template

Every leaf brief emitted by `/swarm` follows this shape. `/swarm-review` parses these fields directly and will fail audit if any are missing or malformed.

A brief is the *entire* context a leaf agent receives. Nothing else. No project overview, no rationale, no description of sibling leaves. The minimum that lets the leaf finish its slice without needing to make a decision.

---

## Format

```markdown
---
leaf_id: leaf-NN
spec_file: <path to spec>
spec_lines: <start>-<end>
test_file: <single test file path>
impl_file: <single impl file path — owned by this leaf>
# Optional plural forms (use ALONGSIDE singular when a leaf legitimately
# spans multiple files — e.g. pgTAP unit+integration test pair, or an
# adapter that needs a tiny __init__.py re-export):
# test_files:
#   - tests/db/test_fn_X_unit.sql
#   - tests/db/test_X_integration.sql
# impl_files:
#   - src/pkg/__init__.py
#   - src/pkg/adapter.py
contract_imports:
  - <fully-qualified symbol from locked type contract>
  - <fully-qualified symbol from locked type contract>
do_not_edit:
  - <glob or path>
  - <glob or path>
impl_line_budget: <int>
test_assertion_budget: <int>
# Optional: who writes the RED test. Default `leaf` (leaf owns both test
# and impl). Set to `parent` for projects where parent-agent authors the
# umbrella + integration tests and the leaf only writes impl. When
# `parent`, the test_file is NOT subject to the parent-owned glob check
# and other briefs don't need to include it in their do_not_edit.
# test_owned_by: parent | leaf
# Optional: parallelism wave. Default 1. Leaves in different waves run
# sequentially (e.g. wave-2 follow-up edits a file wave-1 already owned).
# Cross-wave leaves skip overlap + do_not_edit checks against each other.
# wave: 1
---

## Task

<One-paragraph imperative description. Must reference spec_lines for any
behavioral claim. Must not contain ambiguous verbs (decide, choose, design,
determine, figure out, resolve, "as appropriate").>

## Acceptance

Run `<test command>` for this test_file. Confirm RED. Implement in impl_file
only. Confirm GREEN. Commit the two files. Stop.

## Escalation triggers

Stop and report to the parent if:
- A type the test imports is not in contract_imports.
- The impl would need to create a new file.
- The impl would need to edit a file in do_not_edit.
- Two sibling assertions seem to require contradictory behavior.
- Impl approaches impl_line_budget with assertions still failing.

## Assumption log

If at any point during your run you had to **infer** something the brief did not specify (a default value, an error code, a representation choice, anything), write it to `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` before you commit. Format:

```markdown
## Assumptions made during leaf-NN

- **<thing>**: <inferred value> — source: <which spec line / contract symbol / file you looked at, or "no source — pure guess">
```

Do not bury inferences inside impl comments. The parent runs an assumption-sweep across all leaves before any merge — that sweep only sees the .ASSUMPTIONS.md files. An undocumented inference cannot be swept.
```

---

## What `/swarm-review` checks per brief

| Field | Check |
|---|---|
| `leaf_id` | Unique across briefs in this decomposition. |
| `spec_file` | Exists, is in `spec_dir`. |
| `spec_lines` | Range is concrete (two integers), not "TBD" / "see above" / empty. |
| `test_file`, `impl_file` | One singular each (required). Plural `test_files` / `impl_files` may add more. Combined set not in any same-wave sibling brief. Impl paths not in parent-owned globs. Test paths not in parent-owned globs UNLESS `test_owned_by: parent`. |
| `contract_imports` | All symbols resolve in the locked type contract file. |
| `do_not_edit` | Includes every same-wave sibling's leaf-owned files; includes parent-owned globs. (Sibling test files only required here when `test_owned_by` is `leaf`.) |
| `test_owned_by` (optional) | `parent` or `leaf`. Default `leaf`. |
| `wave` (optional) | Integer ≥ 1. Default 1. Cross-wave leaves are sequenced, not parallel. |
| `impl_line_budget`, `test_assertion_budget` | Set, ≤ project max from `.claude-swarm.toml`. |
| Task prose | No ambiguous verbs from the configured list. |

A brief that fails any of these checks blocks the entire decomposition. The parent restructures and re-emits before any leaf is spawned.

---

## Why this template

The brief is the contract between parent and leaf. If the parent encodes the slice correctly here, the leaf has no surface on which to make a design decision. If the parent encodes it incorrectly, the audit catches it before the leaf gets to act on it. Both failure modes (toes-stepping, design-leak) reduce to malformed briefs; sizing is the third axis the budgets enforce.
