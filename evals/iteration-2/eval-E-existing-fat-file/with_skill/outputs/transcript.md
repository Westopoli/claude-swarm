# /tdd-root Execution Transcript — eval-E-existing-fat-file

## Step 0: Intake

**Mode**: Non-interactive. Recording all answers to ASSUMPTIONS.md.

Intake answers resolved:

| Q  | Answer | Source |
|----|--------|--------|
| 1. Spec file | `inputs/specs/wave-3.md` | Explicit in invocation |
| 2. Wave | 3 | Spec filename + title |
| 3. Expected leaf count | 3 | Three ACs in spec |
| 4. Strategy doc | N/A — not provided | Eval scenario omits; no bible path in config |
| 5. Strategy changes | Unknown | No source |
| 6. Out of scope | `validate_ops`, `order_ops`, `batch_emit` integration | Spec lines 27-31 |
| 7. Brief reviewer | `/tdd-review` only | Default |
| 8. New or existing files | **Modifying existing** | Explicit in invocation prompt |

All assumptions written to `ASSUMPTIONS.md`. Proceeding to Step 1.

---

## Step 1: Locate config

Config file read: `inputs/.tdd-cascade.toml`

Key values extracted:
- `spec_dir` = `"specs"`
- `briefs_dir` = `"briefs"`
- `type_contract_path` = `"src/myproj/types.py"`
- `umbrella_test_cmd` = `"python -m pytest tests/test_umbrella.py -v"`
- `max_impl_lines` = 200
- `max_test_assertions` = 20
- `parent_owned_globs` = `["src/myproj/types.py", "tests/test_umbrella.py", "tests/conftest.py"]`
- `ambiguous_verbs` = `["decide", "choose", "design", "determine", "figure out", "pick", "resolve", "as appropriate"]`
- `extra_spec_gate_cmds` = (not present — default empty)

Config located and valid. Continuing.

---

## Step 2: Spec gate

**Spec file confirmed**: `inputs/specs/wave-3.md` exists and is in `spec_dir`.

**Extra gate commands**: Config has no `[gates]` section and no `extra_spec_gate_cmds`. No commands to run. Gate passes.

---

### Fat-file check (triggered because intake Q8 = "modifying existing")

**File examined**: `inputs/src/myproj/sync_ops.py`

**Reading the file:**

The file's own docstring states:
> "~280 lines covering three distinct behaviors."

Actual file body ends at line 174. Whether 174 or 280, the structural assessment is the same:

**Top-level functions/classes found:**
1. `ContactRow` (dataclass)
2. `TagRow` (dataclass)
3. `CustomFieldRow` (dataclass)
4. `SyncOp` (dataclass)
5. `emit_ops()` — god-function; contains three distinct behavioral branches:
   - Upsert logic (AC1 scope)
   - Tag logic (AC2 scope)
   - Custom-field logic (AC3 scope)
6. `validate_ops()` — out-of-scope per spec
7. `order_ops()` — out-of-scope per spec
8. `_build_upsert_payload()` — helper
9. `_normalize_tag_name()` — helper
10. `_validate_field_key()` — helper
11. `_format_field_value()` — helper
12. `batch_emit()` — out-of-scope per spec

**AC coverage per the spec:**
- AC1 (upsert) → lines 49-63 in `emit_ops()`
- AC2 (tag) → lines 65-79 in `emit_ops()`
- AC3 (custom field) → lines 81-93 in `emit_ops()`

All three ACs that the spec decomposes into **separate leaf assignments** live inside one function in one file. The file's own header declares it as a fat file covering three distinct behaviors.

**Fat-file heuristic check:**
- File is ~174-280 lines (self-described as ~280): meets or approaches >200-line threshold
- File contains branches across three distinct behaviors the spec maps to three separate leaf ACs: YES

**Verdict: Fat-file warning fires.**

---

> **Fat-file warning:** `src/myproj/sync_ops.py` is ~280 lines (self-described) and covers AC1 (upsert emission), AC2 (tag emission), and AC3 (custom-field emission) — which you plan to assign to three separate leaves. Two resolution paths:
>
> **(a) Sequential waves** — assign the leaf covering AC1 as wave 1, AC2 as wave 2, AC3 as wave 3. Same file, one owner at a time. Parallelism eliminated; each leaf modifies the same `emit_ops()` body sequentially. Risk: wave-N leaf must understand wave-(N-1) leaf's edits before writing its own.
>
> **(b) Prep-step split** — parent commits a refactor that splits `emit_ops()` into three sub-functions (`_emit_upsert_ops()`, `_emit_tag_ops()`, `_emit_field_ops()`) in separate modules (or at least in clearly delimited sections) before decomposition. Each sub-function then maps cleanly to one leaf. The dispatcher `emit_ops()` becomes a thin router that the parent owns and does not assign to any leaf. See "Prep steps" in `~/.claude/skills/tdd-cascade-shared/references/playbook.md`.
>
> **Stop here** and ask the user which path to take. Do not pick silently — this is an architectural decision.

---

**STOPPED. Waiting for user input on resolution path before continuing to Steps 3-7.**

Steps 3 (type contract), 4 (umbrella test), 5 (dependency map), 6 (emit briefs), and 7 (hand off) are **not executed** — the skill halted at the fat-file warning as required by the procedure.

---

## What would have come next (if user had answered)

### If user chose (a) Sequential waves:
- Step 3: Read type contract, note symbols
- Step 4: Run umbrella test, confirm RED
- Step 5: Dependency map — all three leaves touch same file, sequential waves prevent collision
- Step 6: Emit three briefs with `wave: 1`, `wave: 2`, `wave: 3` respectively; each brief's `do_not_edit` excludes cross-wave siblings' test files (cross-wave leaves skip overlap checks per template)
- Step 7: Hand off to /tdd-review

### If user chose (b) Prep-step split:
- Parent would need to refactor `sync_ops.py` first, splitting `emit_ops()` into `_emit_upsert_ops()`, `_emit_tag_ops()`, `_emit_field_ops()` before any brief is emitted
- Decomposition restarts after prep-step commit
- Step 3-7 would proceed with clean file boundaries, one file per leaf
