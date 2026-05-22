---
name: swarm-review
description: Audit a set of leaf briefs against the three TDD-cascade invariants before any leaf agent is spawned. Use this whenever the user says "review the briefs", "audit the decomposition", "check the leaf scope", "are these slices safe to run in parallel", "verify the leaf assignments", "did the parent overlap anything", "is anything ambiguous", or anytime briefs were just emitted by /swarm or rewritten after a failure. This skill runs a deterministic check script first — it must never substitute LLM judgment for the script's verdict. Always run this skill before spawning leaves; you'd rather catch overlap/design-leak/oversized-leaf failures at audit time than during execution.
---

# /swarm-review — 3-invariant audit on leaf briefs

This skill is **read-only**. It does not modify briefs, code, tests, or config. It runs a deterministic script and renders the result. The script is the source of truth; this skill's job is to invoke it and explain failures.

If you find yourself wanting to "be lenient" or "use judgment" on a finding, stop. The whole reason this skill exists is to remove judgment from the gate. If the script flags a brief, the parent restructures and re-emits before any leaf spawns.

The companion theory lives at `~/.claude/skills/swarm-shared/references/playbook.md`. The brief schema the audit checks against is at `~/.claude/skills/swarm-shared/references/brief-template.md`.

## 0. Intake — ASK BEFORE PROCEDURE

Before running the check script, lock the scope of this audit so the findings can be interpreted correctly.

**If the invocation is interactive:**

Ask the user as a single block:

1. **Which briefs directory?** (Default: `briefs_dir` from `.claude-swarm.toml`.)
2. **Single wave or multi-wave audit?** A *wave* is a sequential batch of parallel leaves; wave N+1 runs after all wave-N leaves merge and may re-edit wave-N-owned files. Multi-wave changes how `non-overlap` is interpreted (waves are sequential — leaf-04 in wave 1 may legitimately own a file leaf-12 in wave 2 also touches).
3. **Were these briefs just emitted by `/swarm`, or were they hand-edited after a prior FAIL?** Hand-edits without re-running `/swarm` can re-introduce drift the original procedure caught.
4. **Anything you already know is borderline?** (E.g., "leaf-09 is intentionally on the edge of the sizing budget — flag if you must but it's an explicit choice.") Borderline cases the user has already signed off on can be Advisory rather than blocking.

Restate scope in one sentence and wait for confirmation.

**If non-interactive:**

Record an assumption log at `<briefs_dir>/REVIEW_ASSUMPTIONS.md` listing every inferred answer with its source. The downstream parent assumption-sweep (see `/swarm`) will surface drifts.

## Procedure

### 1. Run the check script

From the project's git root, run:

```bash
python ~/.claude/skills/swarm-shared/scripts/check_invariants.py
```

Optional: `--briefs-dir <path>` to override config, `--root <path>` to override git-root detection.

The script reads `<git_root>/.claude-swarm.toml`, parses every `*.md` in `briefs_dir`, and prints one line per brief plus a summary. Exit 0 = all pass, exit 1 = at least one finding, exit 2 = config error.

### 2. Render the output verbatim

Show the user the script's output. Do **not** rewrite findings into your own words. The findings are designed to be diagnostic — the leaf_id, invariant name, and reason all matter for the parent to fix the brief.

### 3. Diagnose, do not fix

For each failure:
- Read the named brief.
- Tell the user which line in the brief triggered the finding.
- Suggest the *category* of fix (e.g., "this brief needs to be split into two — one for `parse()` and one for `validate()`"), but do not edit the brief yourself. Brief edits belong to `/swarm` (or the user) so the next audit run starts from a consistent state.

### 4. Verdict

End the turn with one of:

> **PASS** — N briefs pass. You may now spawn leaf agents.

> **FAIL** — N briefs fail (`leaf-XX`, `leaf-YY`, …). Restructure and re-emit via `/swarm`, then re-run `/swarm-review`. Do not spawn any leaf until this reports PASS.

When the FAIL is caused by **non-overlap** (two briefs claim the same impl file), always append the resolution options so the parent has a clear path forward:

> **Resolution options for overlap on `<file>`:**
> - **(a) Sequential waves** — keep both leaves but assign them different wave numbers. Wave-1 leaf owns the file; wave-2 leaf inherits it after wave-1 merges. Parallelism is reduced but the cascade stays intact.
> - **(b) Prep-step split** — before re-emitting briefs, the parent commits a refactor that splits `<file>` into sub-files (one per leaf's scope). Each leaf then owns a distinct file. Parallelism is preserved. See "Prep steps" in `~/.claude/skills/swarm-shared/references/playbook.md` for the umbrella-before/after requirement.
>
> Do not choose between these — present both to the user. The seam-axis decision (how to split, or whether to serialize) belongs to the parent + human, not to this skill.

## What the three invariants catch

| Invariant | Failure mode it prevents | Where it shows up in a brief |
|---|---|---|
| **non-overlap** | Two leaves stepping on each other's files; race conditions on merge. | Same `impl_file` or `test_file` in two briefs; brief touching a `parent_owned` glob; `do_not_edit` missing a sibling's owned file. |
| **no-design** | Leaf inventing types, choosing API shape, resolving spec ambiguity. | `spec_lines` non-concrete; `contract_imports` referencing symbols not in the locked contract; ambiguous verbs in task prose. |
| **sizing** | Leaf gets a slice too large to finish in one pass, midway it starts making decisions to bridge gaps. | `impl_line_budget` or `test_assertion_budget` over the project max. |

## When you may go beyond the script

Only the script's verdict gates the cascade. You *may* additionally flag observations that aren't yet encoded as invariants — they go in an `Advisory` block after the verdict:

> **Advisory** (not blocking): leaf-03's impl file lives outside the package root; check that's intentional.

Advisory text never changes the verdict. If the user wants an advisory to start blocking, the rule belongs in `check_invariants.py` or `.claude-swarm.toml`, not in your prose.

## Why this skill is script-first

Three failure modes recurring across many decompositions means a human (or an LLM) keeps missing them — they are exactly the kind of check that wants to be mechanical. The script is fast, deterministic, and runs the same way every time. The skill's value is wrapping that check in the cascade's vocabulary so the parent agent knows what to do with each finding. LLM-as-judge is the wrong shape for this gate.
