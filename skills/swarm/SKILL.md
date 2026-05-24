---
name: swarm
description: Bootstrap a TDD parallel-agent decomposition. Use whenever the user wants to slice a spec into leaves, decompose into parallel sub-agent tasks, kick off the cascade, or otherwise begin the umbrella-RED → leaf-decomposition flow. Triggers on phrases like "decompose this spec", "split into leaves", "begin parent agent flow", "set up the umbrella test", "give me the leaf briefs". This skill writes leaf brief files; it does not write impl code. Always pair with /swarm-review before spawning any leaf.
---

# /swarm — bootstrap the TDD cascade

This skill takes the user from a locked spec to a set of leaf briefs ready for parallel sub-agents. It is **not** a code-writing skill. The output of this skill is brief files on disk + an instruction to run `/swarm-review`.

The companion theory lives at `~/.claude/skills/swarm-shared/references/playbook.md`. Read it when you need the *why*. For the canonical brief shape, read `~/.claude/skills/swarm-shared/references/brief-template.md`. For config, read `~/.claude/skills/swarm-shared/references/config.md`.

## 0. Intake — ASK BEFORE PROCEDURE

Before step 1, lock the scope of this batch. The questions below exist because the most common cascade failure mode starts with one of these answers being **inferred** by the parent agent instead of stated by the user.

**If the invocation is interactive** (you can ask and wait):

Ask the user the 7 questions below as a single block. Skip a question only if the user already answered it explicitly in the invoking prompt. Do not infer answers from file context — silent inference is how parents drift from intent.

1. **Which spec file?** Path under `spec_dir/`. If multiple plausible specs exist, list them and ask.
2. **Which wave of this spec?** (1, 2, ...). A *wave* is a sequential batch of parallel leaves; wave 2 can edit files wave 1 already owned. Drives the `wave` field on every brief.
3. **Expected leaf count, order of magnitude?** (3 / 10 / 20?). If the dependency map in step 5 suggests >2× your estimate either way, stop and reconcile with the user before emitting briefs — count mismatch is the earliest signal that the parent and user are picturing different decompositions.
4. **Strategy doc / source-of-truth design doc path?** (the "strategy doc"). You will read this before step 2's spec gate to check spec-vs-strategy-doc alignment.
5. **Anything new in the strategy doc since the last decomposition?** A one-liner from the user is enough; affects whether prior brief conventions still hold.
6. **Anything intentionally out of scope for this batch?** So you do not propose leaves for it.
7. **Who reviews the briefs?** Just `/swarm-review`, or human + `/swarm-review`? Affects how cautious to be on borderline slicing calls.
8. **New files or modifying existing ones?** Are the impl files this batch will produce new files, or modifications to files that already exist in the repo? If modifying existing files, you will run a fat-file check in step 2 — the user does not need to know what that check entails, just whether existing files are in play.

Restate the scope in two sentences and **wait for confirmation** before continuing to step 1.

**If the invocation is non-interactive** (single prompt, no opportunity to ask — e.g., a sub-agent task or a CI run):

Proceed without asking, but maintain an `ASSUMPTIONS.md` file at `<briefs_dir>/ASSUMPTIONS.md`. Record every inferred answer in this format:

```markdown
## Assumptions made during /swarm

- **spec_file**: <inferred value> — source: <which file/clue you read>
- **wave**: <inferred value> — source: <...>
- **expected_leaf_count**: <inferred value> — source: <...>
- **strategy_doc_path**: <inferred value> — source: <...>
- **strategy_changes_since_last**: unknown — no source available
- **out_of_scope**: <inferred> — source: <...>
- **brief_reviewer**: assumed /swarm-review only — source: default
- **existing_files**: <yes/no — inferred from whether planned impl paths already exist in repo>
```

Every assumption is a candidate for the **parent assumption-sweep** (see end of this file). Do not bury inferences inside step 6 brief prose — log them here where a downstream sweep can find them.

## Procedure

Run these steps in order. Stop at the first failure and report.

### 1. Locate config

- Find project root: walk up from the current working directory until a `.claude-swarm.toml` file or a directory that looks like a project root (e.g., contains `src/`, `specs/`, or similar) is found. Do not run any git commands.
- Read `<project_root>/.claude-swarm.toml`. If missing, copy `~/.claude/skills/swarm-shared/templates/.claude-swarm.toml.example` to `<project_root>/.claude-swarm.toml` and ask the user to set `type_contract_path` before continuing. Don't guess.

### 2. Spec gate

- Confirm a spec file in `spec_dir` is named (ask the user if ambiguous — never pick one silently).
- Run every command in `[gates].extra_spec_gate_cmds`. Any non-zero exit = gate fail. Report which command and exit code.
- This skill exports `$SPEC_FILE` before running each gate so project-specific gate scripts can reference the chosen spec.
- **Fat-file check (only if intake Q8 = "modifying existing"):** For each impl file the spec implies will be touched, read the file and count its lines and top-level functions/classes. If any single existing file appears to cover more than one planned leaf's scope (rough heuristic: >200 lines AND contains branches across multiple distinct behaviors the spec decomposes into separate ACs — acceptance criteria, abbreviated AC throughout), flag it:

  > **Fat-file warning:** `<path>` is `N` lines and covers ACs X, Y, Z which you plan to assign to separate leaves. Two resolution paths:
  > - **(a) Sequential waves** — assign leaf covering AC-X as wave 1, leaf covering AC-Y as wave 2. Same file, one owner at a time. Parallelism reduced.
  > - **(b) Prep-step split** — parent commits a refactor that splits `<path>` into sub-files before decomposition. Each sub-file then maps cleanly to one leaf. See "Prep steps" in `~/.claude/skills/swarm-shared/references/playbook.md`.
  >
  > **Stop here** and ask the user which path to take. Do not pick silently — this is an architectural decision.

  If the file is small or covers only one leaf's scope, no warning needed. Continue.

### 3. Shared type contract

- Read `type_contract_path`. If missing, stop and tell the user the contract must exist before decomposition. Do not draft one — that's a design decision and belongs to the parent agent + human review.
- Note the symbols defined (classes, top-level functions, UPPER constants, Pydantic `Literal` members). These form the allowlist for leaf `contract_imports`.

### 4. Umbrella test

- Run `umbrella_test_cmd`. Capture stdout/stderr.
- The test **must fail** (RED). If it passes, abort with the message: "Umbrella is green before any leaf — the cascade has nothing to do. Check that the umbrella encodes the spec's acceptance criteria, not stub passes."
- If the umbrella file doesn't exist, stop and ask the user where it should live; do not invent a location.

**Behavioral-strength heuristic.** Read the umbrella test file(s). For each test function, classify assertions:

- *Source-grep*: assertion is on a string derived from `open(<path>).read()` or `Path(<path>).read_text()` — i.e., the test is checking that a source file *contains* a pattern, not that a behavior is correct.
- *Behavioral*: assertion is on the return value of an imported function call, or on side-effects after invocation.

If >50% of assertions in any umbrella test are source-grep, render:

> ⚠ Weak umbrella: `<test_function>` has N source-grep assertions vs M behavioral. A test that greps file contents passes if the source *looks right* and fails only on rename — it cannot catch the case where the file has the right text but the behavior is wrong. The post-merge apex test (`apex_test_cmd`) is the second-chance gate, but a behavioral umbrella catches gaps earlier. Add at least one assertion on the return value of an imported call before continuing.

This is a heuristic warning, not a hard block by default. The user can override: "proceed anyway, apex test will cover behavioral side." Record the override in `<briefs_dir>/ASSUMPTIONS.md` so the wave-sweep sees it.

### 5. Dependency map

- If `graphify_cmd` is set, run it and inspect the output for files that two planned slices would both touch.
- If empty, fall back to a manual import-graph scan of the impl files you intend to assign. List adjacency in your reasoning so `/swarm-review` can confirm.

### 6. Emit leaf briefs

For each slice you've identified:
- Write `<briefs_dir>/leaf-NN.md` following the template at `~/.claude/skills/swarm-shared/references/brief-template.md` exactly.
- One test file + one impl file per brief. (Plural `test_files` / `impl_files` permitted when the slice legitimately spans more than one file — see template.)
- `do_not_edit` must include every other brief's owned files, plus the parent-owned globs from config.
- `contract_imports` may only reference symbols you found in step 3.
- `spec_lines` must be a concrete `int-int` range citing the spec.
- Task prose: imperative, references spec_lines, no ambiguous verbs (decide / choose / design / determine / figure out / pick / etc.).
- Set `impl_line_budget` and `test_assertion_budget` from config defaults; tighten if you can.
- The brief template already contains the three coordination protocols (sibling-ASSUMPTIONS read, question ledger, contract proposals). Do not strip those sections — they are what convert silent inference into traceable, gated inference.

### 7. Hand off

End your turn with exactly this instruction to the user:

> Briefs written to `<briefs_dir>`. Run `/swarm-review` next. Do not spawn any leaf agents until `/swarm-review` reports `all PASS`.

## What this skill must not do

- Write impl code. Ever. That's the leaf's job, gated by `/swarm-review` + the brief itself.
- Edit the shared type contract. Type changes are a separate, human-reviewed step.
- Make architectural decisions silently. If two slicing strategies are equally valid, present both and ask. Silent picks are how "the agent made a design decision" creeps in at the *parent* level.
- Skip a gate because it's "obviously fine." The gates exist because the obvious turned out to be wrong before — once a gate has caught a real failure, the cost of running it for every subsequent decomposition is trivial compared to the cost of the failure it prevents.

## Parent assumption-sweep

This section runs **after** all leaves report green, before any `/swarm-merge` is invoked. The parent agent (you, if you spawned the leaves) sweeps every leaf's assumption log and your own intake assumption log for drift before merging.

### Inputs

- `<briefs_dir>/ASSUMPTIONS.md` — your own (parent) inferences from intake, if intake was non-interactive.
- For each leaf-NN, `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` — assumptions the leaf agent recorded during its run. Leaves are instructed by their brief to write this file if they had to infer anything.

If a leaf produced no assumption log, that's fine — it means the brief was fully concrete. The sweep is only as long as the union of all log files.

### What to look for

Read every entry across all logs. Flag any entry that matches one of these patterns:

1. **Contradicts the spec.** Assumption picks a value the spec explicitly contradicts. (E.g., spec says "use SQL," leaf assumes pandas.)
2. **Contradicts the strategy doc.** Assumption picks a value the strategy doc explicitly forbids.
3. **Cross-leaf contradiction.** Two leaves made incompatible assumptions about the same shared interface (e.g., leaf-04 assumes the cache returns `None` on miss, leaf-07 assumes it returns `{}`).
4. **Fabricated symbol or path.** Assumption references a type, function, file, or config key that does not exist in the type contract or repo.
5. **Compounded inference.** A leaf assumption is justified by *another* assumption rather than by a spec line or contract symbol. Layered guesses compound at scale.

### Output

Produce a single report with this structure. Do **not** revert or re-merge unilaterally — present to the user.

```markdown
# Assumption-sweep report

## Summary
- Total assumptions logged: N
- Flagged: M (1=contradicts-spec, 2=contradicts-strategy-doc, 3=cross-leaf, 4=fabricated, 5=compounded)
- Unflagged: N-M (recorded for transparency, no drift detected)

## Flagged entries

### [leaf-04 / category 3 (cross-leaf)]
- Assumption: "cache returns None on miss"
- Conflicts with leaf-07's: "cache returns empty dict on miss"
- **Damage assessment:** leaf-07's tests pass with empty-dict assumption but break at merge if leaf-04's path runs first. Estimated blast radius: 1 integration test, 2 dashboard rendering paths.
- **Patch suggestion (no redo):** Decide canonical miss-value at the parent level (recommended: None, matches spec line 138). Update leaf-07's impl + test to match. Re-run leaf-07's test only. Other leaves unaffected.

### [leaf-09 / category 4 (fabricated)]
...
```

Always include damage assessment + patch suggestion. The user makes the call on whether to patch or redo. Default bias: patch, do not redo — redo costs an afternoon, a patch usually costs minutes.

If zero entries flag, report:

> Assumption-sweep clean. N assumptions reviewed, none drift. Proceed to /swarm-merge for each leaf.

## Why this skill exists

Three failure modes recur in parallel-agent TDD work: leaves stepping on each other's files, leaves quietly making design decisions, and leaves receiving tasks too big to finish coherently. The cascade structurally prevents all three — but only if the parent assigns leaves correctly. This skill is the procedure for doing that correctly. The audit (`/swarm-review`) is the safety net that catches mistakes before any leaf spawns. The merge protocol (`/swarm-merge`) is the safety net that catches mistakes after the leaf is done. Three commands, three safety nets, one cascade.
