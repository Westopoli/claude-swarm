---
name: swarm-merge
description: Run the post-leaf merge protocol after a TDD-cascade leaf agent reports green. Use whenever the user says "merge this leaf", "leaf-NN is done, integrate it", "the agent reports green", "bring this back into main", "run the umbrella after this branch", or any time a leaf finishes and its two-file diff is ready to land. This skill verifies the diff is exactly two files, reruns the umbrella, regenerates the dependency map, and reverts the merge if the umbrella regresses. Always use this in place of an ad-hoc git merge for leaf branches — ad-hoc merges silently re-introduce the failure modes the cascade prevents.
---

# /swarm-merge — post-leaf merge protocol

A leaf finished. Its two-file diff is on a branch (or in a worktree). This skill verifies the diff is well-formed, runs the umbrella, and either merges + advances or reverts + reports. Merges are **event-driven**: leaf reports green, this skill runs once, the next leaf merge happens on its own cycle. No batching.

The companion theory lives at `~/.claude/skills/swarm-shared/references/playbook.md`.

## 0. Intake — ASK BEFORE PROCEDURE

Before locating the diff, confirm the merge's place in the broader cascade.

**If the invocation is interactive:**

Ask the user as a single block:

1. **Which leaf?** (leaf-NN identifier, or branch / worktree path.)
2. **What did the leaf state as its scope?** (One-liner; you'll check the diff matches this, not just the brief.)
3. **Is this part of a multi-merge sequence?** If yes, the umbrella baseline you compare against is the *post-previous-merge* state, not the original root.
4. **Was a parent assumption-sweep run yet?** (See `/swarm` "Parent assumption-sweep".) If not and the cascade had >5 leaves or any non-interactive leaf runs, recommend running it before merging this leaf — it's cheaper to surface a contradiction now than after the umbrella runs.
5. **Expected umbrella delta?** (E.g., "should add 2 passes.") A delta that doesn't match expectation is a yellow flag even if the count went up.

Restate scope in one sentence and wait for confirmation.

**If non-interactive:**

Record an assumption log at `<briefs_dir>/leaf-NN.MERGE_ASSUMPTIONS.md` listing inferred answers. Surface in your final report.

## Procedure

### 0.5 Retroactive bypass check

Before touching the leaf branch, verify no sibling leaf landed on `main` outside this protocol.

- Run `git log <prior-wave-close-commit>..main --oneline` (use the wave's root commit as the lower bound; if unknown, ask the user).
- For each commit, regex-match the message against the leaf-NN pattern (e.g. `leaf-\d+`, `leaf-NN`, or whatever naming the briefs use).
- Cross-reference against briefs in `<briefs_dir>`: a commit whose message matches a known leaf but has no corresponding `/swarm-merge` gate record is a bypass.
- If any bypass found, print at the top of the report **before continuing**:

> ⚠ BYPASS DETECTED: `<hash>` `<message>` — this leaf committed directly to main without a gate run. The two-file rule and brief-match were never verified for it. Confirm whether to audit it now or accept the risk before proceeding.

Do not silently continue past a detected bypass.

### 1. Locate the leaf diff

- Ask the user which branch / worktree / commit range to merge if it isn't obvious from context.
- Run `git diff --name-only <base>...<head>`. Capture the file list.
- **Base-divergence check:** Run `git merge-base <leaf-head> main`. If the result is not equal to `main HEAD`, surface:

> ⚠ Leaf base is N commits behind main. Choose before continuing:
> - **(r) Rebase** leaf onto current main, then re-run this skill.
> - **(c) Cherry-pick** leaf commits onto main directly.
> - **(x) Abort** — investigate manually.

This is an explicit user choice. Do not silently pick a strategy.

### 2. Two-file rule

The diff **must** touch exactly two files:
- One test file.
- One impl file.

If it touches more, or fewer, or one of either kind:

> **Reject.** Diff touches N files (`a`, `b`, `c`). A leaf owns exactly one test + one impl. Send the agent back; do not merge.

This is non-negotiable. A leaf that needed to touch a third file made a design decision (or stepped on parent-owned infrastructure) — both failure modes the cascade explicitly prevents. The right fix is either re-slicing the brief or escalating to the parent for a contract change.

**Forensic history check:** Even when the two-file count is clean, verify the leaf branch history wasn't rewritten:

- Run `git log <base>..<head> --diff-filter=AM --name-only` and confirm only the two expected files appear across all commits.
- Check reflog: run `git rev-parse <branch>@{push} 2>/dev/null`. If this diverges from the current branch tip, the branch was force-pushed. Surface:

  > ⚠ Possible force-push on leaf branch. Forensic confidence low — history may have been rewritten after the agent reported green.

### 3. Confirm the two files match the brief

- Read the brief at `<briefs_dir>/leaf-NN.md`.
- The diff's two files must equal the brief's `test_file` and `impl_file` exactly.
- Path mismatch → reject. The leaf cannot rename.

### 4. Run the umbrella

- Run `umbrella_test_cmd` from config **twice**: once on the pre-merge state (or use a kept baseline), once after applying the leaf diff.
- Capture **named per-test results** from both runs, not just counts. For pytest, add `-v --tb=no -q` if not already in the command to get one `PASSED`/`FAILED` line per test. For other runners, capture whatever named output is available.
- If the runner emits no per-test names (only a summary count), record that explicitly: `step 4: per-test names unavailable — regression detection will be count-only (weaker gate)`.
- **Brief acceptance gate:** Parse the brief at `<briefs_dir>/leaf-NN.md` for an `Acceptance:` or `## Acceptance` block. If a test command is specified there, run it as a second independent gate. Both the umbrella and the brief's acceptance command must pass. If the brief has no acceptance block, render: `step 4: brief acceptance gate skipped (no Acceptance block in brief)`.

### 4.5 Assumption sweep (hard gate)

This step runs after the umbrella and before any merge decision.

- Read `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` for the leaf being merged.
- List all assumption files for already-merged siblings in `<briefs_dir>` (files matching `leaf-??.ASSUMPTIONS.md` whose leaf was previously merged).
- If a contradiction exists between the merging leaf's assumptions and any sibling's assumptions (e.g., leaf-02 assumes "users table has no `deleted_at`" and leaf-04 assumed "users table has `deleted_at`") → **block merge**, list every conflict explicitly.
- If no contradictions: continue.
- If no `leaf-NN.ASSUMPTIONS.md` exists for this leaf, note it but do not block.

### 5. Decide

First, regardless of net count, check for **per-test regressions**:

- Compute `regressed = pre_passing_tests − post_passing_tests` (tests that were passing before and are now failing).
- If `regressed` is non-empty → **revert immediately**, regardless of net delta. Continue to step 7. Report each regressed test by name.

  > ⚠ Regression detected: `<test-name>` was passing before merge and is now failing. Net delta is irrelevant — a previously-stable test broke. Reverting.

  This catches the case where a leaf adds 3 new passes but breaks 1 prior-wave assertion: net +2 looks clean but a regression landed.

- If per-test names were unavailable (count-only mode flagged in step 4): skip the set-diff check and fall through to count comparison, but emit: `⚠ Per-test regression check skipped (count-only mode). Count-based gate only — prior-wave regressions may go undetected.`

Then check net count and expected delta:

- **More assertions pass than before:** check expected delta (from intake Q5). If actual delta matches expected → merge. If actual delta is positive but doesn't match expected (e.g., expected +3, actual +5), issue yellow flag:

  > ⚠ Delta mismatch: expected +N, got +M. Leaf may have covered sibling territory. Verify scope before merging.

  Confirm with user before proceeding.
- **Same number of assertions pass:** the leaf's behavior wasn't load-bearing for the umbrella. That's possible (the slice may have been for an integration boundary), but it's a yellow flag. Warn the user and confirm before merging.
- **Fewer assertions pass than before:** revert. Continue to step 7 (regression).

### 6. Merge + regen map

- Merge the leaf branch (`git merge --ff-only` if the branch is rebased; otherwise a regular merge — never `--squash` because the audit trail wants the two-file commit preserved).
- If `graphify_cmd` is set, run it. Inspect the diff in the dependency map for **unexpected couplings**: an import path that wasn't present in pre-merge graph, or a new edge between two leaf-owned modules. Flag for the user — a coupling that wasn't in the design is the leaf making a structural decision. If `graphify_cmd` is not set, render: `step 6: graph-coupling check skipped (graphify_cmd not configured)` — do not silently skip.

### 7. Regression path

- Revert the merge: `git revert -m 1 <merge-commit>` (or `git reset --hard <base>` if the merge hasn't been pushed — confirm with the user before running `reset --hard`).
- Append a `## Merge regression` block to the brief file noting which umbrella assertion regressed and what the leaf's diff did.
- End the turn with: "Leaf-NN is back on the assignment list. Restart it with the appended note."

## What this skill must not do

- Squash or rewrite the leaf's commit. The two-file commit is the audit trail; flattening it removes the structural evidence that the cascade was followed.
- Apply hand-edits to the leaf's diff to make the umbrella pass. If the leaf's diff doesn't make the umbrella pass, the leaf is wrong — send it back, don't patch around it.
- Skip the umbrella run because "the change is small." Every merge runs the umbrella. If the umbrella takes too long, that's a project-level problem (slice the umbrella, parallelize CI), not a reason to skip the gate.
- Batch multiple leaves. One leaf → one umbrella run → one merge or one revert. Batching is how regressions become hard to attribute.

## Why this skill is event-driven

The umbrella is the only signal that a merge made forward progress. Running it after every leaf — not after a batch — keeps the attribution clean. If leaf-04 's merge regressed an assertion, you know immediately. If leaves 03–07 batched and one of them regressed, you're bisecting. The skill is the friction that makes the cheap path (one-at-a-time) also the default path.
