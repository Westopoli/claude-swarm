---
name: swarm-post-review
description: Run the post-leaf post-review protocol after a TDD-cascade leaf agent reports green. Use whenever the user says "admit this leaf", "post-review this leaf", "leaf-NN is done, integrate it", "the agent reports green", "validate and admit", "leaf finished, admit it", "audit and admit leaf NN", or any time a leaf finishes and its staged diff is ready to land. Also use when the user says "post-review the queue", "admit all pending leaves", or wants to admit multiple leaves at once — invoke queue mode (/swarm-post-review queue) which pre-validates all leaves in parallel then admits them sequentially with a full umbrella run per leaf. This skill verifies the staged files exactly match the brief's declared `test_files` + `impl_files` (none parent-owned), runs the umbrella pre and post, checks per-test regressions by name, and restores the originals if the umbrella regresses. Always use this in place of an ad-hoc file copy for leaf work — ad-hoc copies silently re-introduce the failure modes the cascade prevents.
---

# /swarm-post-review — post-leaf post-review protocol

A leaf finished. Its staged files sit in `.swarm/pending/leaf-NN/`. This skill validates the staged files against the brief, copies them to their destinations, runs the umbrella, and either admits the leaf or reverts by restoring from backup. No git commands are issued. All state lives in `.swarm/`.

A leaf brief declares its file footprint via plural `test_files` and `impl_files` frontmatter (typically one test + one impl, but a leaf may own multiple files if the brief explicitly lists them). The staging directory must match that declaration exactly — same count, same paths.

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
      <test_files[*] path>      ← leaf's test files, mirroring dest paths from root
      <impl_files[*] path>      ← leaf's impl files, mirroring dest paths from root
  backups/
    leaf-NN/
      <test_files[*] path>      ← originals before copy (written by skill at step 6)
      <impl_files[*] path>
  questions/
    leaf-NN-Q<n>.md             ← published mid-run question (leaf wrote, parent may answer)
  answers/
    leaf-NN-Q<n>.md             ← parent's answer; presence flips the question to resolved
  proposals/
    leaf-NN.md                  ← leaf-proposed change to a parent-owned file (status: pending/accepted/rejected)
  escalations/
    leaf-NN.md                  ← leaf escalation; required when a brief escalation-trigger fires
  wave-NN.snapshot.json         ← hashes of every non-leaf-owned file at wave start (G5 source of truth)
  wave-NN.SWEEP.md              ← parent's aggregate assumption-sweep report; required before first admission of wave
  post-review-log.md            ← append-only audit trail; skill writes, never human
```

Leaf agents are instructed (via their brief) to write output to `.swarm/pending/leaf-NN/` using paths that mirror the destination from the project root. Example: if `impl_files` contains `src/cache.py`, the staged file lives at `.swarm/pending/leaf-03/src/cache.py`.

---

## 0. Intake — ASK BEFORE PROCEDURE

Before reading the staging directory, confirm the admission's place in the broader cascade.

**If the invocation is interactive:**

Ask the user as a single block:

1. **Which leaf?** (leaf-NN identifier.)
2. **What did the leaf state as its scope?** (One-liner; you'll check the staged files match this.)
3. **Is this part of a multi-leaf admission sequence?** If yes, the umbrella baseline you compare against is the *post-previous-admission* state, not the wave root.
4. **Expected umbrella delta?** (E.g., "should add 2 passes.") A delta that doesn't match expectation is a yellow flag even if the count went up.

Restate scope in one sentence and wait for confirmation.

**If non-interactive:**

Record an assumption log at `<briefs_dir>/leaf-NN.POST_REVIEW_ASSUMPTIONS.md` listing inferred answers. Surface in your final report.

---

## Procedure

### 0.4 Wave assumption-sweep required (G7)

The parent's aggregate assumption-sweep (procedure in `/swarm-spawn` SKILL.md) is a separate document from per-leaf post-review sweep. It runs **across all leaves of the wave** before any leaf is admitted and surfaces cross-leaf drift no per-leaf check sees.

Determine the admitting leaf's wave (from brief frontmatter, default `1`). Search `post-review-log.md` for prior entries from this same wave:

- If **no prior entries** for this wave (this is the first admission of the wave): require `.swarm/wave-<wave>.SWEEP.md` to exist. If missing → **block**:

> ⚠ G7: this is the first admission of wave `<wave>`, but no parent assumption-sweep file at `.swarm/wave-<wave>.SWEEP.md` exists. The aggregate sweep must run before any leaf of the wave is admitted. See `/swarm-spawn` SKILL.md "Parent assumption-sweep" for procedure.

- The sweep file's mtime must be newer than every `leaf-NN.ASSUMPTIONS.md` for this wave. Otherwise → **block**:

> ⚠ G7: wave-sweep file exists but is older than at least one leaf ASSUMPTIONS entry (leaf-XX modified after sweep). Re-run the sweep — leaf-XX's assumptions were not included.

- If prior entries for this wave exist (subsequent admission): skip this gate, the wave-sweep already passed at first admission.

### 0.5 Bypass check

Before touching staging, verify every prior leaf in `briefs_dir` was gated through this protocol.

- Read `.swarm/post-review-log.md`.
- List all `leaf-NN.md` files in `briefs_dir` whose leaf_id predates the leaf being admitted now (based on NN ordering).
- Any prior leaf_id absent from `post-review-log.md` is a bypass — it was never gated.
- If any bypass found, print **before continuing**:

> ⚠ BYPASS DETECTED: `leaf-NN` has a brief in `briefs_dir` but no entry in `post-review-log.md`. It was never gated through this protocol. The file-match rule, parent-owned check, and umbrella were never verified for it. Confirm whether to audit it now or accept the risk before proceeding.

Do not silently continue past a detected bypass.

**Audit trail integrity:** Before reading `post-review-log.md`, verify the file begins with the required header (see step 6 for format). If the header is missing or the file has been manually edited (entries out of timestamp order, entries deleted), warn:

> ⚠ post-review-log.md integrity check failed. The audit trail may have been tampered with. Do not rely on bypass detection until the log is restored.

### 0.7 Wave-snapshot init (first admission of wave only)

If this is the first admission of the wave (same condition as G7 above), compute SHA-256 of **every file in the repo that is not declared in any wave-N brief's `test_files` + `impl_files`**. Write the map to `.swarm/wave-<wave>.snapshot.json`:

```json
{
  "wave": <wave>,
  "created_at": "<ISO timestamp>",
  "leaf_owned_paths": ["src/cache.py", "tests/test_cache.py", ...],
  "hashes": {
    "<path>": "<sha256>",
    ...
  }
}
```

If `.swarm/wave-<wave>.snapshot.json` already exists, skip this step — it was written at first admission.

Skip files matching common ignore patterns (`.git/**`, `.swarm/**`, `__pycache__/**`, `node_modules/**`, `.venv/**`). Configurable via optional `.claude-swarm.toml` key `snapshot_ignore`.

### 1. Verify staging directory

- Confirm `.swarm/pending/leaf-NN/` exists.
- List all files in the staging directory (recursive). This is the leaf's claimed diff.
- If staging directory is missing or empty → stop:

> Staging directory `.swarm/pending/leaf-NN/` not found or empty. Leaf must write its output there before this skill runs.

### 2. File-match rule

Read the brief at `<briefs_dir>/leaf-NN.md`. Take the union of its `test_files` and `impl_files` frontmatter lists (both are plural lists; a list of one is fine). Call this set `declared`.

The staging directory **must** contain exactly the files in `declared` — same count, same paths (relative to project root). No extras, no missing, no renames.

- **Count mismatch:**

> **Reject.** Staging contains N files; brief declares M (`test_files` + `impl_files`). Leaf cannot add or drop files relative to its brief. Send the agent back; do not admit.

- **Path mismatch (same count, different paths):**

> **Reject.** Staged file `<path>` is not in the brief's declared footprint. Leaf cannot rename or relocate files. Send the agent back.

Most leaves declare one test + one impl. A leaf may declare multiple files only if its brief explicitly lists them — `/swarm-review` is what authorises that shape; `/swarm-post-review` enforces it. The cascade invariant is "no surprise files at admission", not literally "two files".

**Parent-owned check (G1):** After the file-match check passes, verify **no** staged file matches a glob in `parent_owned` from `.claude-swarm.toml`. Run this per-file across every staged path.

> **Reject.** `<file>` matches parent-owned glob `<glob>`. Leaf cannot touch parent territory. Send the agent back.

This is non-negotiable. A leaf that needed to touch a parent-owned file made a design decision the cascade explicitly forbids. The right fix is escalating to the parent for a contract change.

### 3. Brief frontmatter sanity

The file-match check in step 2 already validates staging against the brief. Step 3 is a cheap sanity pass on the brief itself:

- If `test_files` or `impl_files` is missing, empty, or non-list → reject. The brief is malformed; the cascade cannot enforce ownership against an unspecified footprint.
- If any path in either list is absolute, escapes the project root (`..`), or duplicates a path in the other list → reject. Footprints must be unambiguous, project-relative paths.

### 4. ASSUMPTIONS file check (G2)

- Check whether `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` exists.
- If it does: note how many assumptions are logged. It will be cross-referenced in step 6.5.
- If it does not: note its absence. This is expected when the brief was fully concrete — do not block.
- The skill does **not** proceed if the brief references an ASSUMPTIONS file that is expected but provably missing (e.g., leaf ran non-interactively per brief but no log was written). In that case:

> ⚠ Brief indicates non-interactive run but no `leaf-NN.ASSUMPTIONS.md` found. Leaf may have inferred without logging. Confirm before proceeding.

### 4.1 Open-question check (G3)

Leaves may publish questions to `.swarm/questions/leaf-NN-Q<n>.md` instead of inferring silently. The parent answers asynchronously in `.swarm/answers/leaf-NN-Q<n>.md`. This gate enforces that every published question has been resolved before its leaf is admitted.

- List `.swarm/questions/leaf-NN-Q*.md`.
- For each question file, require **one** of:
  - A matching `.swarm/answers/leaf-NN-Q<n>.md` (parent answered).
  - An entry in `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` explicitly tagged `question: leaf-NN-Q<n>, unanswered: true` acknowledging the leaf proceeded under inference.
- If neither exists → **block**:

> ⚠ G3: leaf-NN published question `leaf-NN-Q<n>.md` that is unanswered AND not acknowledged in ASSUMPTIONS. Either answer the question or have the leaf log it as `unanswered: true` before admitting.

- If an answer exists, parse it for a `decision: <value>` line. Compare against any matching entry in ASSUMPTIONS. If the leaf's recorded inference contradicts the parent's answer → **block**:

> ⚠ G3: leaf-NN inferred `<value>` for question Q<n>; parent answered `<other-value>`. Leaf's code was written under the wrong assumption. Send back with the corrected answer.

This is the gate that converts "silent inference" into "logged inference with explicit parent acknowledgement". The cascade does not lose async; it gains traceability.

### 4.2 Contract-proposal check (G4)

Leaves that need a parent-owned file changed must not edit it (G1 blocks that). Instead, the leaf writes `.swarm/proposals/leaf-NN.md` with a proposed diff and proceeds with its remaining work. This gate enforces that proposals are explicitly resolved before admission.

- Check whether `.swarm/proposals/leaf-NN.md` exists.
- If it does, parse its `status:` frontmatter. Allowed values: `pending` | `accepted` | `rejected` | `superseded`.
- If status is `pending` → **block**:

> ⚠ G4: leaf-NN filed an unresolved contract proposal at `.swarm/proposals/leaf-NN.md`. Parent must accept, reject, or supersede before admission. Accepted proposals require the parent to first apply the diff to the parent-owned target file.
- If status is `accepted`, verify the target parent-owned file actually contains the proposed change (grep for an identifying line from the proposal's diff). If not present → **block**:

> ⚠ G4: leaf-NN's proposal is marked accepted but the change was never applied to `<target>`. Apply the change first, then re-run post-review.

- If status is `rejected` or `superseded`: log the fact and proceed. The leaf may need to be re-spawned if its impl depended on the rejected change — that is a separate parent call, not this gate's concern.

### 4.3 Wave-snapshot integrity check (G5)

Catches leaves that wrote to files outside their declared footprint by direct Write tool use — bypassing the staging dir.

- Load `.swarm/wave-<wave>.snapshot.json`. If absent → **block** (snapshot should have been written at first admission; absence means the wave skipped 0.7).
- For every path in `hashes`, recompute SHA-256 of the current file on disk.
- If any hash drifted → **block** with the diff:

> ⚠ G5: wave-snapshot integrity violated. The following non-leaf-owned files changed since wave start:
> - `<path>`: snapshot SHA `<a>`, current SHA `<b>`
> - ...
>
> Some leaf wrote outside its declared footprint, OR the parent edited a file mid-wave without re-snapshotting. Identify the writer, revert the unauthorised change, or update the wave brief and re-snapshot. Do not admit until the snapshot is clean.

- **Permitted exception:** a path that appears in *this leaf's* `test_files` + `impl_files` is allowed to differ (the leaf is the legitimate owner via staging). The check applies only to paths outside the admitting leaf's footprint.

This gate is **detection, not prevention**. The skill cannot revoke Write permission from sub-agents. It can only refuse to admit when a violation is evident. Treat any G5 hit as a leaf-discipline failure to investigate, not a routine warning to dismiss.

### 4.4 Escalation-trigger detection (G6)

Briefs list escalation triggers in their `## Escalation triggers` section. Some triggers can be detected mechanically from staged code (signature change, new file creation, cross-function reuse) and the brief may declare `detect:` commands for each trigger (see brief-template.md).

- Parse the admitting leaf's brief for an `escalation_triggers:` frontmatter list. Each entry may have a `detect:` shell command.
- For each entry with a `detect:` command, run it from project root with `$STAGING_DIR` set to `.swarm/pending/leaf-NN/`.
- If a `detect:` command exits 0 (trigger condition matched) AND no `.swarm/escalations/leaf-NN.md` exists → **block**:

> ⚠ G6: escalation trigger `<trigger-name>` fired (detect command exited 0) but no `.swarm/escalations/leaf-NN.md` was filed. The brief said this condition required escalation; the leaf either ignored the trigger or buried the decision. Investigate before admission.

- If a `detect:` command matches AND an escalation file exists: log "escalation acknowledged", continue.
- If no `detect:` commands are declared on the brief: skip this gate. Triggers without `detect:` rely on leaf self-report and cannot be mechanically verified.

### 5. Run the umbrella — pre-admission

- Run `umbrella_test_cmd` from config **before** copying staging files.
- Capture **named per-test results**: for pytest add `-v --tb=no -q` if not already present to get one `PASSED`/`FAILED` line per test. For other runners, capture whatever named output is available.
- If runner emits no per-test names (count only): record `step 5: per-test names unavailable — regression detection will be count-only (weaker gate)`.
- Record: `pre_passing_tests` = set of named passing tests, `pre_count` = total passing.

### 6. Copy staged files + run umbrella post-admission

- For **every** path in the brief's `test_files` + `impl_files`: if a file currently exists at that path, snapshot it to `.swarm/backups/leaf-NN/<path>` (mirroring the destination layout). If no file exists at the destination yet (new file), record that fact — the revert step will delete it instead of restoring.
- For **every** staged file under `.swarm/pending/leaf-NN/`: copy it to its destination path. Every declared file must be copied; no partial admissions.
- Run `umbrella_test_cmd` again (post-admission state).
- Capture `post_passing_tests` and `post_count`.
- **Brief acceptance gate (G7):** Parse `<briefs_dir>/leaf-NN.md` for an `## Acceptance` block. If a test command is specified, run it as a second independent gate. Both umbrella and brief acceptance command must pass. If no acceptance block: render `step 6: brief acceptance gate skipped (no Acceptance block in brief)`.

### 6.5 Assumption sweep (hard gate)

This step runs after the post-admission umbrella and before the admission decision.

- Read `<briefs_dir>/leaf-NN.ASSUMPTIONS.md` for the leaf being admitted.
- List all `leaf-??.ASSUMPTIONS.md` files for already-admitted siblings (those with entries in `post-review-log.md`).
- If a contradiction exists between this leaf's assumptions and any sibling's assumptions → **block**, list every conflict explicitly.
- If no contradictions: continue.
- If no `leaf-NN.ASSUMPTIONS.md` exists: note it, do not block.

### 7. Decide

**Per-test regression check first (regardless of net count):**

- Compute `regressed = pre_passing_tests − post_passing_tests`.
- If `regressed` is non-empty → **revert immediately**. Continue to step 8.

> ⚠ Regression detected: `<test-name>` was passing before admission and is now failing. Net delta is irrelevant — a previously-stable test broke. Reverting.

- If per-test names were unavailable (count-only mode): skip set-diff, emit `⚠ Per-test regression check skipped (count-only mode). Count-based gate only — prior-wave regressions may go undetected.`

**Net count + expected delta:**

- **More assertions pass than before:** check expected delta (from intake Q4). If actual matches expected → admit (step 8 admit path). If actual is positive but doesn't match expected, issue yellow flag:

> ⚠ Delta mismatch: expected +N, got +M. Leaf may have covered sibling territory. Verify scope before admitting.

  Confirm with user before proceeding.
- **Same number of assertions pass:** yellow flag. Possible the slice was for an integration boundary, but confirm before admitting.
- **Fewer assertions pass than before:** revert. Continue to step 8 revert path.

### 8a. Admit

- Staged files are already in place (copied in step 6).
- Delete `.swarm/pending/leaf-NN/` (staging is consumed).
- If `post-review-log.md` does not yet exist, create it with this exact header before appending:

```
# Post-Review Log — append-only, do not edit manually
# Editing this file invalidates bypass-detection. Each entry written by /swarm-post-review only.

| leaf_id | files | delta | timestamp | status |
|---------|-------|-------|-----------|--------|
```

- Append one row. List every file in `impl_files` + `test_files`, comma-separated:

```
| leaf-NN | <impl_files[*]>, <test_files[*]> | +N | <ISO timestamp> | clean |
```

  The log is append-only. Never edit, reorder, or delete entries. The bypass check in step 0.5 depends on the log being an accurate, ordered record of every gated admission. Integrity is verified by the header presence and timestamp ordering.

- If `graphify_cmd` is set, run it. Inspect the dependency map diff for unexpected couplings — a new import edge between leaf-owned modules that wasn't in the design. Flag for the user. If `graphify_cmd` is not set, render: `step 8: graph-coupling check skipped (graphify_cmd not configured)`.

### 8b. Revert

- For every backup under `.swarm/backups/leaf-NN/`: overwrite the matching destination path with the backup contents.
- For every declared file that did **not** have a backup (new file, recorded in step 6): delete it from the destination tree.
- Delete `.swarm/pending/leaf-NN/` (staging consumed — leaf must re-stage if it tries again).
- Append to `post-review-log.md`:

```
| leaf-NN | <impl_files[*]>, <test_files[*]> | REVERTED | <ISO timestamp> | regression: <test-name> |
```

- Append a `## Post-review regression` block to `<briefs_dir>/leaf-NN.md` noting which test regressed and what the staged diff did.
- End the turn with: "Leaf-NN is back on the assignment list. Restart it with the appended note."

---

## Queue mode — `/swarm-post-review queue`

Processes all pending leaves automatically: pre-validates every leaf in parallel (fast failure across all), then admits them sequentially with a full umbrella run per leaf. One command replaces N invocations without sacrificing regression attribution.

### Intake for queue mode

Ask as a single block before doing anything:

1. **Which wave?** Confirm all pending leaves belong to the same wave.
2. **Umbrella baseline?** If some leaves were already admitted this session, the baseline is post-last-admission state, not the wave root.
3. **Expected total delta?** Sum across all leaves. Per-leaf mismatches still trigger individual yellow flags.

If non-interactive: log a `QUEUE_ASSUMPTIONS.md` in `briefs_dir` with inferred answers. Proceed.

### Phase 1 — Parallel pre-validation

Before any files are copied, validate every leaf under `.swarm/pending/` simultaneously. For each leaf, run:

- **Step 0.5 bypass check (queue-aware):** A bypass is a leaf whose brief exists, whose NN is less than the smallest NN in the current queue, and that has no pending dir AND no post-review-log entry. A leaf currently in the queue is not a bypass — it is staged and waiting. Flag genuine bypasses before proceeding.
- **Step 1** — staging dir exists and non-empty
- **Step 2** — file-match rule (staged set equals brief's `test_files` + `impl_files`) + G1 parent-owned check per-file
- **Step 3** — brief frontmatter sanity (`test_files`/`impl_files` present, well-formed, project-relative, non-overlapping)
- **Step 4** — G2 ASSUMPTIONS file check
- **Step 4.1** — G3 open-question check (every published question is answered OR acknowledged in ASSUMPTIONS)
- **Step 4.2** — G4 contract-proposal check (no `pending` proposals; accepted proposals are actually applied)
- **Step 4.3** — G5 wave-snapshot integrity (no drift in non-leaf-owned files)
- **Step 4.4** — G6 escalation-trigger detection (any matching `detect:` command requires a filed escalation)

Additionally, queue mode enforces the wave-level gates **once** before the per-leaf loop:

- **Step 0.4** — G7 wave-sweep file exists and is newer than all leaf ASSUMPTIONS
- **Step 0.7** — wave-snapshot init (writes `.swarm/wave-N.snapshot.json` if absent)

Collect all failures across all leaves. If any leaf fails pre-validation:

> Pre-validation failed for N leaves:
> - leaf-07: tests/umbrella_extended.py matches parent-owned glob tests/umbrella*.py
> - leaf-12: staged file does not match brief footprint (src/foo.py not in declared impl_files/test_files)
> - leaf-19: staging directory empty
> - leaf-22: G3 — published question Q1 is unanswered and not acknowledged in ASSUMPTIONS
> - leaf-27: G4 — proposal status is `pending`; parent must resolve before admission
> - leaf-31: G5 — wave-snapshot integrity violated: src/auth.py drifted (this leaf doesn't declare it)
> - leaf-34: G6 — escalation trigger `signature_change` fired but no `.swarm/escalations/leaf-34.md` filed
>
> Fix all failures before re-running /swarm-post-review queue. No files have been copied.

If all pass: print `Pre-validation passed for N leaves. Beginning sequential admission.`

### Phase 2 — Sequential admission

Process leaves in ascending NN order. For each leaf, run steps 5–8 exactly as in single-leaf mode (pre-umbrella, copy, post-umbrella, acceptance gate, assumption sweep, decide, admit or revert).

**On admit:** continue to next leaf.

**On revert:** stop immediately.

> Queue stopped at leaf-NN — regression detected: `<test-name>` was passing before this admission and is now failing. N leaves remain pending. Fix leaf-NN and re-run `/swarm-post-review queue`.

Never skip a failed leaf and continue. A regression in the middle corrupts the umbrella baseline for every subsequent leaf.

### Apex test (queue completion gate)

After all leaves in the queue are admitted cleanly, run `apex_test_cmd` from config (if set). This is a **behavioral integration test**, distinct from the per-leaf umbrella. The umbrella verifies each leaf's slice in isolation; the apex verifies the leaves *compose* — that no per-leaf RED→GREEN illusion masks a behavioral gap at the integration boundary.

- If `apex_test_cmd` is unset: render `apex test: skipped (apex_test_cmd not configured)`. Encourage user to configure one in `.claude-swarm.toml` if the project has meaningful integration behavior.
- If set, run it. **Apex failure does not auto-revert** — at this point multiple leaves are admitted, and identifying which leaf caused the apex failure is a separate forensic step. Block + report:

> ⚠ Apex failure after queue admission. The leaves passed per-leaf umbrella isolation but the integration test failed. The cascade composed but the behavior did not. Investigate which admitted leaf introduced the behavioral gap (likely candidate: any leaf with a source-grep-only umbrella assertion — see /swarm-spawn step 4 behavioral-umbrella check, or /swarm step 8 if discovery ran upstream).

The apex gate is what catches the failure mode where a leaf's umbrella was a regex check on file source rather than a behavioral assertion. Per-leaf umbrellas can pass while integration fails; the apex test is the place where that gap becomes loud.

### Queue completion report

When all leaves are admitted cleanly AND the apex test passes (or is unconfigured), print:

```
Queue complete — N leaves admitted. Apex: <PASS | skipped | FAILED>.

| leaf    | delta | status |
|---------|-------|--------|
| leaf-01 | +2    | clean  |
| leaf-02 | +1    | clean  |
| ...     |       |        |

Total delta: +N assertions
```

---

## What this skill must not do

- Edit `post-review-log.md` except by appending. Never reorder, correct, or remove entries. The log's integrity is the only tamper-detection mechanism.
- Copy files outside of the staging-to-destination path. Skill touches exactly the destination files declared in the brief's `test_files` + `impl_files` — no more, no fewer.
- Skip the umbrella run because "the change is small." Every admission runs the umbrella.
- Admit multiple leaves under a single umbrella run. Queue mode runs one umbrella per leaf — that per-leaf attribution is the point. Never collapse multiple leaves into one umbrella pass.
- Proceed past a bypass warning without explicit user confirmation.
- Answer a leaf's published question by editing `.swarm/answers/` on the leaf's behalf. Answers are parent decisions; this skill only verifies their presence and consistency.
- Mark a contract proposal `accepted` without the parent first applying the diff. G4 catches the mismatch — do not silently re-mark.

---

## Why no git

Git commands require permission grants that may not be available in all agentic contexts, and git state (branches, worktrees, rebase conflicts) has proven to be a source of cascade-disrupting side effects when agents run non-interactively. The file-based model is equivalent in guarantees:

- **Staging dir** replaces the branch: leaf work is isolated until gated.
- **Backup dir** replaces `git revert`: originals are snapshotted before any copy.
- **post-review-log.md** replaces `git log`: ordered, append-only, human-readable audit trail.
- **Per-test set-diff** replaces reliance on commit metadata for regression attribution.

The three invariants (non-overlap, no design decisions, sizing) are enforced identically. The only thing lost is cryptographic commit signing — acceptable given the trust model of a single-project cascade.

---

## File-mediated async coordination

The cascade is a tree, not a graph. Leaves never communicate directly with each other; all coordination is mediated through files the parent arbitrates. Three mechanisms exist (see `~/.claude/skills/swarm-shared/references/playbook.md` for theory):

- **Sibling-ASSUMPTIONS read** — leaves may *read* (never write) other leaves' `leaf-??.ASSUMPTIONS.md`. Catches drift at leaf-time instead of admission-time. No skill enforcement: it is a brief-boilerplate behavior the leaf executes before logging its own inference.
- **Question ledger** — leaf publishes `.swarm/questions/leaf-NN-Q<n>.md`; parent answers in `.swarm/answers/leaf-NN-Q<n>.md`. **G3 gate** above enforces resolution before admission.
- **Contract proposals** — leaf publishes `.swarm/proposals/leaf-NN.md` instead of editing parent-owned files. **G4 gate** above enforces explicit parent resolution before admission.

None of these introduces leaf-to-leaf messaging. None introduces shared mutable state. None synchronously blocks any leaf. The cascade stays tree-shaped and regression attribution stays single-leaf.

---

## Why queue mode preserves attribution

Queue mode runs one umbrella per leaf, sequentially. If leaf-07 regresses a test, the queue stops at leaf-07 and names the test. The remaining leaves are untouched. You fix exactly one thing.

Contrast with a true batch (one umbrella for N leaves): a failure could be caused by any of the N admissions, or by their interaction. You're bisecting instead of reading a report.

Pre-validation runs in parallel because structural failures (wrong file count, parent-owned violation, brief mismatch) are detectable without the umbrella and don't affect each other. Running them concurrently gives you all failures at once before any admission starts — no waiting 20 leaves to discover leaf-23 staged a parent-owned file.

The invariant: one umbrella run per leaf admitted, always. Queue mode automates the sequence; it does not collapse it.
