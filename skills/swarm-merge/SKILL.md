---
name: swarm-merge
description: Run the post-leaf merge protocol after a TDD-cascade leaf agent reports green. Use whenever the user says "merge this leaf", "leaf-NN is done, integrate it", "the agent reports green", "bring this back into main", "run the umbrella after this branch", or any time a leaf finishes and its two-file diff is ready to land. Also use when the user says "merge all leaves", "merge the queue", "process all pending", or wants to merge multiple leaves at once — invoke queue mode (/swarm-merge queue) which pre-validates all leaves in parallel then merges sequentially with a full umbrella run per leaf. This skill verifies staged files are exactly two (neither parent-owned), runs the umbrella pre and post, checks per-test regressions by name, and restores the originals if the umbrella regresses. Always use this in place of an ad-hoc file copy for leaf work — ad-hoc copies silently re-introduce the failure modes the cascade prevents.
---

# /swarm-merge — post-leaf merge protocol

A leaf finished. Its two files sit in `.swarm/pending/leaf-NN/`. This skill validates the staged files, copies them to their destinations, runs the umbrella, and either finalises or reverts by restoring from backup. No git commands are issued. All state lives in `.swarm/`.

The companion theory lives at `~/.claude/skills/swarm-shared/references/playbook.md`.

---

## Directory layout

```
.swarm/
  briefs/
    leaf-NN.md                  ← brief for this leaf
    leaf-NN.ASSUMPTIONS.md      ← leaf's assumption log (if any inferences made)
  pending/
    leaf-NN/
      <test_file path>          ← leaf's test file, mirroring dest path from root
      <impl_file path>          ← leaf's impl file, mirroring dest path from root
  backups/
    leaf-NN/
      <test_file path>          ← original before copy (written by skill at step 4)
      <impl_file path>
  merge-log.md                  ← append-only audit trail; skill writes, never human
```

Leaf agents are instructed (via their brief) to write output to `.swarm/pending/leaf-NN/` using paths that mirror the destination from the project root. Example: if `impl_file` is `src/cache.py`, the staged file lives at `.swarm/pending/leaf-03/src/cache.py`.

---

## 0. Intake — ASK BEFORE PROCEDURE

Before reading the staging directory, confirm the merge's place in the broader cascade.

**If the invocation is interactive:**

Ask the user as a single block:

1. **Which leaf?** (leaf-NN identifier.)
2. **What did the leaf state as its scope?** (One-liner; you'll check the staged files match this.)
3. **Is this part of a multi-merge sequence?** If yes, the umbrella baseline you compare against is the *post-previous-merge* state, not the wave root.
4. **Expected umbrella delta?** (E.g., "should add 2 passes.") A delta that doesn't match expectation is a yellow flag even if the count went up.

Restate scope in one sentence and wait for confirmation.

**If non-interactive:**

Record an assumption log at `<briefs_dir>/leaf-NN.MERGE_ASSUMPTIONS.md` listing inferred answers. Surface in your final report.

---

## Procedure

### 0.5 Bypass check

Before touching staging, verify every prior leaf in `briefs_dir` was gated through this protocol.

- Read `.swarm/merge-log.md`.
- List all `leaf-NN.md` files in `briefs_dir` whose leaf_id predates the leaf being merged now (based on NN ordering).
- Any prior leaf_id absent from `merge-log.md` is a bypass — it was never gated.
- If any bypass found, print **before continuing**:

> ⚠ BYPASS DETECTED: `leaf-NN` has a brief in `briefs_dir` but no entry in `merge-log.md`. It was never gated through this protocol. The two-file rule, parent-owned check, and umbrella were never verified for it. Confirm whether to audit it now or accept the risk before proceeding.

Do not silently continue past a detected bypass.

**Audit trail integrity:** Before reading `merge-log.md`, verify the file begins with the required header (see step 6 for format). If the header is missing or the file has been manually edited (entries out of timestamp order, entries deleted), warn:

> ⚠ merge-log.md integrity check failed. The audit trail may have been tampered with. Do not rely on bypass detection until the log is restored.

### 1. Verify staging directory

- Confirm `.swarm/pending/leaf-NN/` exists.
- List all files in the staging directory (recursive). This is the leaf's claimed diff.
- If staging directory is missing or empty → stop:

> Staging directory `.swarm/pending/leaf-NN/` not found or empty. Leaf must write its output there before this skill runs.

### 2. Two-file rule

The staging directory **must** contain exactly two files:
- One test file.
- One impl file.

If it contains more, or fewer, or one of either kind:

> **Reject.** Staging contains N files (`a`, `b`, `c`). A leaf owns exactly one test + one impl. Send the agent back; do not merge.

**Parent-owned check (G1):** Even when count = 2, verify neither file matches a glob in `parent_owned` from `.claude-swarm.toml`. A leaf that staged a parent-owned file passed the count gate but violated ownership.

> **Reject.** `<file>` matches parent-owned glob `<glob>`. Leaf cannot touch parent territory. Send the agent back.

This is non-negotiable. A leaf that needed to touch a parent-owned file made a design decision the cascade explicitly forbids. The right fix is escalating to the parent for a contract change.

### 3. Confirm staged files match the brief

- Read the brief at `<briefs_dir>/leaf-NN.md`.
- The staging directory's two files must equal the brief's `test_file` and `impl_file` paths exactly (relative to project root).
- Path mismatch → reject. The leaf cannot rename or relocate files.

### 4. ASSUMPTIONS file check (G2)

- Check whether `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` exists.
- If it does: note how many assumptions are logged. It will be cross-referenced in step 4.5.
- If it does not: note its absence. This is expected when the brief was fully concrete — do not block.
- The skill does **not** proceed if the brief references an ASSUMPTIONS file that is expected but provably missing (e.g., leaf ran non-interactively per brief but no log was written). In that case:

> ⚠ Brief indicates non-interactive run but no `leaf-NN.ASSUMPTIONS.md` found. Leaf may have inferred without logging. Confirm before proceeding.

### 5. Run the umbrella — pre-merge

- Run `umbrella_test_cmd` from config **before** copying staging files.
- Capture **named per-test results**: for pytest add `-v --tb=no -q` if not already present to get one `PASSED`/`FAILED` line per test. For other runners, capture whatever named output is available.
- If runner emits no per-test names (count only): record `step 5: per-test names unavailable — regression detection will be count-only (weaker gate)`.
- Record: `pre_passing_tests` = set of named passing tests, `pre_count` = total passing.

### 6. Copy staged files + run umbrella post-merge

- Snapshot the current versions of `test_file` and `impl_file` to `.swarm/backups/leaf-NN/`, mirroring destination paths. These are the restore targets if regression is detected.
- Copy `.swarm/pending/leaf-NN/<test_file>` → `<test_file>` and `.swarm/pending/leaf-NN/<impl_file>` → `<impl_file>`.
- Run `umbrella_test_cmd` again (post-merge state).
- Capture `post_passing_tests` and `post_count`.
- **Brief acceptance gate (G7):** Parse `<briefs_dir>/leaf-NN.md` for an `## Acceptance` block. If a test command is specified, run it as a second independent gate. Both umbrella and brief acceptance command must pass. If no acceptance block: render `step 6: brief acceptance gate skipped (no Acceptance block in brief)`.

### 6.5 Assumption sweep (hard gate)

This step runs after the post-merge umbrella and before the merge decision.

- Read `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` for the leaf being merged.
- List all `leaf-??.ASSUMPTIONS.md` files for already-merged siblings (those with entries in `merge-log.md`).
- If a contradiction exists between this leaf's assumptions and any sibling's assumptions → **block**, list every conflict explicitly.
- If no contradictions: continue.
- If no `leaf-NN.ASSUMPTIONS.md` exists: note it, do not block.

### 7. Decide

**Per-test regression check first (regardless of net count):**

- Compute `regressed = pre_passing_tests − post_passing_tests`.
- If `regressed` is non-empty → **revert immediately**. Continue to step 8.

> ⚠ Regression detected: `<test-name>` was passing before merge and is now failing. Net delta is irrelevant — a previously-stable test broke. Reverting.

- If per-test names were unavailable (count-only mode): skip set-diff, emit `⚠ Per-test regression check skipped (count-only mode). Count-based gate only — prior-wave regressions may go undetected.`

**Net count + expected delta:**

- **More assertions pass than before:** check expected delta (from intake Q4). If actual matches expected → finalise (step 8 finalise path). If actual is positive but doesn't match expected, issue yellow flag:

> ⚠ Delta mismatch: expected +N, got +M. Leaf may have covered sibling territory. Verify scope before finalising.

  Confirm with user before proceeding.
- **Same number of assertions pass:** yellow flag. Possible the slice was for an integration boundary, but confirm before finalising.
- **Fewer assertions pass than before:** revert. Continue to step 8 revert path.

### 8a. Finalise

- Staged files are already in place (copied in step 6).
- Delete `.swarm/pending/leaf-NN/` (staging is consumed).
- If `merge-log.md` does not yet exist, create it with this exact header before appending:

```
# Merge Log — append-only, do not edit manually
# Editing this file invalidates bypass-detection. Each entry written by /swarm-merge only.

| leaf_id | files | delta | timestamp | status |
|---------|-------|-------|-----------|--------|
```

- Append one row:

```
| leaf-NN | <impl_file>, <test_file> | +N | <ISO timestamp> | clean |
```

  The log is append-only. Never edit, reorder, or delete entries. The bypass check in step 0.5 depends on the log being an accurate, ordered record of every gated merge. Integrity is verified by the header presence and timestamp ordering.

- If `graphify_cmd` is set, run it. Inspect the dependency map diff for unexpected couplings — a new import edge between leaf-owned modules that wasn't in the design. Flag for the user. If `graphify_cmd` is not set, render: `step 8: graph-coupling check skipped (graphify_cmd not configured)`.

### 8b. Revert

- Restore originals from `.swarm/backups/leaf-NN/` → overwrite `<test_file>` and `<impl_file>`.
- Delete `.swarm/pending/leaf-NN/` (staging consumed — leaf must re-stage if it tries again).
- Append to `merge-log.md`:

```
| leaf-NN | <impl_file>, <test_file> | REVERTED | <ISO timestamp> | regression: <test-name> |
```

- Append a `## Merge regression` block to `<briefs_dir>/leaf-NN.md` noting which test regressed and what the staged diff did.
- End the turn with: "Leaf-NN is back on the assignment list. Restart it with the appended note."

---

## Queue mode — `/swarm-merge queue`

Processes all pending leaves automatically: pre-validates every leaf in parallel (fast failure across all), then merges sequentially with a full umbrella run per leaf. One command replaces N invocations without sacrificing regression attribution.

### Intake for queue mode

Ask as a single block before doing anything:

1. **Which wave?** Confirm all pending leaves belong to the same wave.
2. **Umbrella baseline?** If some leaves were already merged this session, the baseline is post-last-merge state, not the wave root.
3. **Expected total delta?** Sum across all leaves. Per-leaf mismatches still trigger individual yellow flags.

If non-interactive: log a `QUEUE_ASSUMPTIONS.md` in `briefs_dir` with inferred answers. Proceed.

### Phase 1 — Parallel pre-validation

Before any files are copied, validate every leaf under `.swarm/pending/` simultaneously. For each leaf, run:

- **Step 0.5 bypass check (queue-aware):** A bypass is a leaf whose brief exists, whose NN is less than the smallest NN in the current queue, and that has no pending dir AND no merge-log entry. A leaf currently in the queue is not a bypass — it is staged and waiting. Flag genuine bypasses before proceeding.
- **Step 1** — staging dir exists and non-empty
- **Step 2** — two-file rule + G1 parent-owned check
- **Step 3** — brief match
- **Step 4** — G2 ASSUMPTIONS file check

Collect all failures across all leaves. If any leaf fails pre-validation:

> Pre-validation failed for N leaves:
> - leaf-07: tests/umbrella_extended.py matches parent-owned glob tests/umbrella*.py
> - leaf-12: staged impl_file does not match brief (src/foo.py ≠ src/bar.py)
> - leaf-19: staging directory empty
>
> Fix all failures before re-running /swarm-merge queue. No files have been copied.

If all pass: print `Pre-validation passed for N leaves. Beginning sequential merge.`

### Phase 2 — Sequential merge

Process leaves in ascending NN order. For each leaf, run steps 5–8 exactly as in single-leaf mode (pre-umbrella, copy, post-umbrella, acceptance gate, assumption sweep, decide, finalise or revert).

**On finalise:** continue to next leaf.

**On revert:** stop immediately.

> Queue stopped at leaf-NN — regression detected: `<test-name>` was passing before this merge and is now failing. N leaves remain pending. Fix leaf-NN and re-run `/swarm-merge queue`.

Never skip a failed leaf and continue. A regression in the middle corrupts the umbrella baseline for every subsequent leaf.

### Queue completion report

When all leaves merge cleanly, print:

```
Queue complete — N leaves merged.

| leaf    | delta | status |
|---------|-------|--------|
| leaf-01 | +2    | clean  |
| leaf-02 | +1    | clean  |
| ...     |       |        |

Total delta: +N assertions
```

---

## What this skill must not do

- Edit `merge-log.md` except by appending. Never reorder, correct, or remove entries. The log's integrity is the only tamper-detection mechanism.
- Copy files outside of the staging-to-destination path. Skill touches exactly two destination files per run.
- Skip the umbrella run because "the change is small." Every merge runs the umbrella.
- Merge multiple leaves under a single umbrella run. Queue mode runs one umbrella per leaf — that per-leaf attribution is the point. Never collapse multiple leaves into one umbrella pass.
- Proceed past a bypass warning without explicit user confirmation.

---

## Why no git

Git commands require permission grants that may not be available in all agentic contexts, and git state (branches, worktrees, rebase conflicts) has proven to be a source of cascade-disrupting side effects when agents run non-interactively. The file-based model is equivalent in guarantees:

- **Staging dir** replaces the branch: leaf work is isolated until gated.
- **Backup dir** replaces `git revert`: originals are snapshotted before any copy.
- **merge-log.md** replaces `git log`: ordered, append-only, human-readable audit trail.
- **Per-test set-diff** replaces reliance on commit metadata for regression attribution.

The three invariants (non-overlap, no design decisions, sizing) are enforced identically. The only thing lost is cryptographic commit signing — acceptable given the trust model of a single-project cascade.

---

## Why queue mode preserves attribution

Queue mode runs one umbrella per leaf, sequentially. If leaf-07 regresses a test, the queue stops at leaf-07 and names the test. The remaining leaves are untouched. You fix exactly one thing.

Contrast with a true batch (one umbrella for N leaves): a failure could be caused by any of the N merges, or by their interaction. You're bisecting instead of reading a report.

Pre-validation runs in parallel because structural failures (wrong file count, parent-owned violation, brief mismatch) are detectable without the umbrella and don't affect each other. Running them concurrently gives you all failures at once before any merge starts — no waiting 20 leaves to discover leaf-23 staged a parent-owned file.

The invariant: one umbrella run per leaf merged, always. Queue mode automates the sequence; it does not collapse it.
