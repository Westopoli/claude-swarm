---
name: swarm
description: First command in the TDD parallel-agent cascade. Discovery step — takes the user from zero (or partial documentation) to a locked spec, a minimal type contract, and a failing umbrella test that pins the cascade's "done" definition. Use whenever the user wants to start a new task, feature, or project and has no spec / no type contract / no umbrella test yet, or has only partial documentation. Triggers on phrases like "I want to build", "let's plan this out", "start a new task", "begin a new feature", "kick off the cascade from scratch", "I have nothing yet, help me plan", "set up the planning for X". This skill writes design artifacts only — spec, type contract, and one behavioral umbrella test. It does NOT write impl code. It does NOT decompose the spec into leaves (that is `/swarm-spawn`, the next step). Every architecture / design decision must be surfaced for explicit user approval or flagged in `.UNSTATED.md` for later resolution — no silent picks.
---

# /swarm — discovery step of the TDD cascade

This skill is the **first** command in the cascade. It is the entry point for users who are starting a task with no prior documentation (or only partial documentation). The output of this skill is three artifacts on disk — a spec file, a type contract file, and a failing umbrella test — each user-approved at an explicit gate, plus an `.UNSTATED.md` companion log for everything the skill inferred that the user did not directly state.

The companion theory lives at `~/.claude/skills/swarm-shared/references/playbook.md`. The downstream decomposition step is `/swarm-spawn`. The pre-leaf audit step is `/swarm-review`. The post-leaf admission step is `/swarm-post-review`.

## Where /swarm fits

**/swarm is the FIRST command in the cascade.** It is optional only in the sense that a user who already has a spec, contract, and umbrella in place may skip directly to `/swarm-spawn`. Cascade order:

```
/swarm          → discovery: drafts spec + type contract + umbrella test (RED).
                  User confirms each artifact at an explicit gate.
                  Hands off to /swarm-spawn.
/swarm-spawn    → decomposition: slices spec into one leaf brief per sub-agent.
                  Hands off to /swarm-review.
/swarm-review   → audits briefs against invariants. Reports PASS/FAIL per brief.
[spawn leaves]  → one sub-agent per brief, in parallel.
/swarm-post-review → runs once per leaf after the leaf reports green. Gated admission.
```

**Inputs to /swarm:** nothing required. The user invokes /swarm at the start of a task. The skill's step-0 intake asks the user what they want to build and whether any prior documentation exists.

**Output of /swarm:**

- a **spec file** at `<spec_dir>/<name>.md` — every line either cites a user statement (`[source: user-stmt-N]`) or is flagged in `<spec_dir>/<name>.UNSTATED.md`.
- a **type contract file** at `<type_contract_path>` — minimal symbols only; each symbol either cites a spec line or lands in `.UNSTATED.md`.
- an **umbrella test** at the path that `umbrella_test_cmd` runs — behavioral assertions only (no source-grep), imports from the type contract, confirmed RED.
- an **unstated-assumptions log** at `<spec_dir>/<name>.UNSTATED.md` — every value the skill picked that the user did not directly state, with a user-supplied disposition (confirm / edit / accept-as-flagged).

**Hand-off**: /swarm does NOT invoke /swarm-spawn. The user (or the parent chat, in a deliberate later turn) invokes /swarm-spawn next.

## Design principle: autonomy classes

The skill's job is to make design choices visible. Every decision the skill takes falls into one of these classes:

| Decision class | Autonomy | Why |
|---|---|---|
| Mechanical drafting (rendering a file once content is user-approved) | Full | Content was approved upstream; rendering is deterministic. |
| Phrasing / wording inside an artifact | Full (user can edit) | Mechanical; user owns the next-edit pass. |
| **Architecture / design choices** (data shapes, behaviors, defaults, error semantics, naming that implies semantics) | **None** | Each surfaces for explicit user approval or lands in `.UNSTATED.md`. This is the failure mode the entire cascade exists to prevent — silent agents picking design. |
| Artifact location (where the spec / contract / umbrella files live) | Read from `.claude-swarm.toml` if set; ask once if missing | Mechanical with one-shot fallback. |

If you find yourself about to pick a value that affects how the system behaves (a default, an error case, a data shape, a naming choice that carries meaning), stop and either ask the user or write it to `.UNSTATED.md`. The whole skill is the procedure for keeping circular grounding safe — and that only works if every design pick is either user-approved or flagged.

## Invocation mode — interactive vs non-interactive

Before step 0, determine which invocation mode applies. This decides what to do when a gate has no human answer available.

- **Interactive** — there is a real human on the other end of this chat turn. The user can reply to questions. This is the default when invoked directly by a user in a fresh chat.
- **Non-interactive** — invoked as a sub-agent task, a CI step, an automated trigger, or in any context where no human-in-the-loop turn signal exists (e.g., the prompt arrived as a single dispatched task with all expected user answers pre-scripted, or no answer channel exists). If a scripted-responses file is present (e.g., `USER_RESPONSES.md` in the working directory), this skill is non-interactive — the script is the canonical user transcript; look up the matching response per gate.

**Declare the mode at the top of your run.** If unsure, treat as non-interactive — silent picks under the assumption of interactivity are worse than over-flagging.

**Non-interactive fallback rule (applies to every gate in the procedure below):** if a gate question has no answer (no script entry, or the script returns `STOP_AND_LOG`), do NOT hang. Record the unresolved question as an entry in `<spec_dir>/<name>.UNSTATED.md` with Disposition `flagged-for-spawn`, then continue. The downstream sweep (`/swarm-spawn` audit) picks up flagged-for-spawn entries. The full theory is at `~/.claude/skills/swarm-shared/references/playbook.md` (section: "Interactive vs non-interactive invocation").

## 0. Intake — ASK BEFORE PROCEDURE

Ask the user as a single block:

1. **What do you want to build?** (one or two paragraphs from the user, in their own words. Open-ended.)
2. **Do you already have any documentation about this task** — notes, design docs, a half-written spec, a paragraph from another chat, anything?
   - **Yes** → user pastes or cites the docs. The skill treats those as the initial pool of user statements (each one tagged `[source: user-doc-N]`), but **still** runs the restate-and-confirm loop on extracted content — extracting from docs is its own inference step.
   - **No** → the skill starts clean. The interview is open-ended.

Restate the answers to both questions in two sentences and **wait for confirmation** before continuing to step 1.

## Procedure

Run these steps in order. Stop at the first user disapproval and revise before continuing.

### 1. Locate config

- Find project root: walk up from the current working directory until a `.claude-swarm.toml` file or a directory that looks like a project root is found.
- Read `<project_root>/.claude-swarm.toml`. If missing, copy `~/.claude/skills/swarm-shared/templates/.claude-swarm.toml.example` to `<project_root>/.claude-swarm.toml`, then walk the user through filling each required field. The bootstrap is not complete after the copy — every field below needs a user-supplied value, not a placeholder:
  - `spec_dir` — directory where the spec file will live (often `specs/`).
  - `briefs_dir` — where `/swarm-spawn`'s leaf briefs will go (default `.swarm/briefs/`).
  - `type_contract_path` — file the contract will be written to (often `src/<pkg>/types.py`).
  - `umbrella_test_cmd` — command that will run the umbrella test you are about to draft (e.g., `pytest tests/umbrella.py`).
  - `parent_owned` — globs for files only the parent can edit downstream.

Do not guess any value. If the user cannot answer a field, stop. Wrong values picked here propagate into every downstream skill.

### 2. Restate-and-confirm loop (gate: `intent-confirmed`)

Paraphrase the user's intent back in your own words, in 2–4 sentences. Ask the user to either:

- **Approve** ("yes, that's it") — proceed to step 3.
- **Correct** ("close, but ...") — incorporate the correction, paraphrase again. Loop.

Do not advance to step 3 until the user explicitly approves. Silent advance is the same failure mode the cascade exists to prevent, expressed at the discovery layer.

### 3. Architecture intake (record user statements)

Ask the user a focused set of questions about the architecture. Tailor the list to the kind of system they are building, but cover at minimum:

1. **What are the key inputs?** (data shapes, types, sources)
2. **What are the key outputs?** (data shapes, types, sinks)
3. **What are the main behaviors / transformations?** (one sentence each — these become acceptance criteria)
4. **What are the explicit constraints?** (performance, language/library choices, conventions to follow)
5. **What is explicitly out of scope?** (so you do not draft a spec line for it)
6. **What does "done" look like for the umbrella test?** (one sentence describing the user-visible behavior the umbrella will assert on)

Store every answer **verbatim** in your working memory, each labeled with a stable id (`[user-stmt-1]`, `[user-stmt-2]`, …). These labels become the citations every spec line and contract symbol uses. Do not paraphrase the user's words at this stage — paraphrasing is itself a design decision and belongs to a later, gated step.

### 4. Draft the spec (gate: `spec-traceable`)

Write `<spec_dir>/<name>.md`. Choose `<name>` from the user's restated intent in step 2 (mechanical — derive from the noun phrase the user used; ask if ambiguous).

**Spec format:**

```markdown
# <name>

## Summary
<one paragraph paraphrasing user-stmt-1 (intent). Cite source.>

## Acceptance criteria
1. <criterion> [source: user-stmt-N]
2. <criterion> [source: user-stmt-N]
...

## Inputs
<bullets, each with source citation>

## Outputs
<bullets, each with source citation>

## Constraints
<bullets, each with source citation>

## Out of scope
<bullets, each with source citation>
```

**Trace-or-flag discipline:** every spec line either ends with `[source: user-stmt-N]` (or `[source: user-doc-N]` for content extracted from prior docs), or it does not appear in the spec — instead it appears in `<spec_dir>/<name>.UNSTATED.md` as a flagged inference (see step 10).

Before writing the file, re-read your draft. If any line lacks a citation, move it to the `.UNSTATED.md` queue. Do not write uncited content into the spec.

### 5. Spec review gate (`spec-approved`)

Render the drafted spec to the user. Ask:

- **Approve** the spec as-is → proceed.
- **Edit** (user describes a change) → apply the edit; if the edit introduces content not traceable to a user statement, log it as a new user-stmt and re-render. Re-ask.
- **Restart** (the spec is fundamentally off) → return to step 2.

Do not proceed to step 6 without an explicit "approve."

### 6. Draft the type contract (gate: `contract-minimal`)

Write the file at `<type_contract_path>`. Include the **minimum** set of symbols needed to encode the spec's inputs, outputs, and main behaviors as type signatures. For each symbol:

- give it a name + signature that the umbrella test (step 8) will import.
- cite the spec line(s) the symbol encodes, e.g., `# encodes spec.md line 14 (input shape)`.
- include a body that is the smallest implementation that lets the umbrella import the symbol without error. Sentinel return values (`raise NotImplementedError`, `return None`, `return SENTINEL`) are correct here — actual behavior lives in leaf impls downstream.

**Trace-or-flag discipline:** every symbol either cites a spec line, or it does not appear in the contract — instead it appears in `.UNSTATED.md` as a flagged inference.

**Minimality discipline:** if you are about to add a symbol the spec does not directly imply (helper types, internal protocols, utility constants), do not. Either ask the user, or flag it in `.UNSTATED.md` and proceed without it. Over-broad contracts are the discovery-layer equivalent of design leak.

### 7. Contract review gate (`contract-approved`)

Render the drafted contract to the user. Ask the same three-way choice as step 5 (approve / edit / restart). Restarting the contract returns to step 6, not step 2 — the spec is already locked.

### 8. Draft the umbrella test (gates: `umbrella-red`, `umbrella-behavioral`)

Write a single behavioral test at the path that `umbrella_test_cmd` will discover. The test:

- imports from the type contract (no symbols outside the contract).
- asserts on **return values** or **observable side effects** of contract symbols — never on source-file contents (no `open(path).read()` assertions).
- encodes at least one acceptance criterion from the spec. Cite which one in a comment.
- is **expected to fail** when run — because the contract has sentinel bodies.

Run `umbrella_test_cmd` to confirm:

- exit code is non-zero (RED) — if it passes, abort with: "Umbrella is green before any leaf. The test does not actually exercise the contract; revise to assert on contract behavior, not on imports or signatures."
- of the assertions present, ≥50% are behavioral (not source-grep). If <50%, render the weak-umbrella warning from `swarm-shared/references/playbook.md` and require the user to confirm proceeding.

### 9. Umbrella review gate (`umbrella-approved`)

Render the umbrella test to the user. Same three-way choice (approve / edit / restart). Restart returns to step 8 — the spec and contract are locked.

### 10. Self-scan production (gate: `unstated-resolved`)

This is the load-bearing step that makes circular grounding safe. Without it, the skill could quietly invent values throughout steps 4–8 and never surface them.

Re-read every artifact produced (spec, contract, umbrella test). For each line, ask: *does this trace back to an explicit user statement from step 3 (or to a prior user-doc citation)?* List every value, default, naming choice, behavior, or invariant for which the answer is **no**.

Categories to look for:

- **Defaults**: any default value (timeouts, sizes, retry counts, fallback behaviors) the user did not state.
- **Naming with semantics**: a field or function name that implies a behavior the user did not describe (e.g., `cache_ttl_seconds` when the user said "cache it").
- **Error semantics**: what happens on invalid input, missing field, network failure — anything the user did not specify.
- **Data-shape choices**: dict vs object, list vs set, JSON dialect, encoding — when the user did not specify.
- **Behavior-on-edge**: what the system does at boundaries the user did not call out.

Write `<spec_dir>/<name>.UNSTATED.md`:

```markdown
# Unstated assumptions for <name>

## Entries

### U-1: <short label>
- Artifact: <spec | contract | umbrella>
- Location: <line ref or symbol name>
- Inferred value: <what the skill picked>
- Why this could not be cited: <e.g., "user did not state a default for X">
- Disposition: <pending — to be set by user>

### U-2: ...
```

For each entry, present it to the user with the three-way choice:

- **Confirm** — accept the inferred value; update Disposition to `confirmed`. The entry stays in `.UNSTATED.md` as a record but is no longer "open."
- **Edit** — user provides a different value. Update the relevant artifact (spec / contract / umbrella) to match, re-cite as `[source: user-stmt-N]` (the user's edit is itself a user statement), update Disposition to `edited`.
- **Accept-as-flagged** — leave the inference in place but mark it as a known assumption for `/swarm-spawn`'s downstream sweep to pick up. Update Disposition to `flagged-for-spawn`.

Do not hand off until **every** entry has a non-`pending` disposition. An unresolved entry is the exact failure mode the cascade exists to prevent: a silent design pick masquerading as a confirmed choice.

If `.UNSTATED.md` would have **zero** entries, render it anyway with a single line: `No unstated assumptions detected.` This forces the explicit scan and confirms it ran.

### 11. Hand off

End your turn with exactly this instruction to the user:

> Spec, type contract, and umbrella drafted at:
> - `<spec_dir>/<name>.md`
> - `<type_contract_path>`
> - `<umbrella test path>`
>
> Unstated-assumptions log at `<spec_dir>/<name>.UNSTATED.md` — all entries resolved.
>
> Run `/swarm-spawn` next. The decomposition step will read the spec, contract, and confirmed-RED umbrella, and emit one leaf brief per parallel sub-agent.

## What this skill must not do

- Write impl code. The only "code" this skill writes is the umbrella test, which is a *behavioral assertion file* — it imports from the contract and asserts on its behavior. It never writes the impl behind those assertions.
- Pick any architecture / design value without surfacing it for user approval (steps 5, 7, 9) or flagging it in `.UNSTATED.md` (step 10). Both options are valid; silence is not.
- Skip step 10 (the unstated-sweep) even if you believe you have nothing to flag. The forced scan is the gate that keeps circular grounding safe.
- Skip any review gate (steps 2, 5, 7, 9) because "the user obviously meant X." Obvious meanings are the precise place silent design picks hide.
- Delegate any drafting step to a sub-agent. The parent chat IS the planning authority. Sub-agents exist only to execute pre-audited leaf briefs after `/swarm-review` passes — and only `/swarm-spawn`'s briefs reach that audit. Drafting via sub-agent reintroduces the failure mode the cascade exists to prevent: a non-overlord making design decisions invisible to the audit. Stock Claude defaults that say "delegate big drafting jobs to protect context" do not apply here.
- Auto-invoke `/swarm-spawn` at the end. Hand-off is an *instruction to the user*, not a side effect. The parent decides when to advance to decomposition.
- Edit any file outside the three artifact paths (spec, contract, umbrella) and their `.UNSTATED.md` companion. In particular, do not create or modify files in `briefs_dir/` — that is `/swarm-spawn`'s territory.
- Continue past a review gate (steps 2, 5, 7, 9, 10) without explicit approval **in interactive mode**. Silence ≠ approval. If the user is unresponsive in interactive mode, stop and wait. **In non-interactive mode**, log the unresolved gate as an `.UNSTATED.md` entry with Disposition `flagged-for-spawn` and continue — do not hang waiting for a human who is not there.
- Run `/swarm-spawn`, `/swarm-review`, or `/swarm-post-review` itself. /swarm's job ends at step 11 — "Hand off."

## Why this skill exists

The cascade structurally prevents three failure modes in parallel-agent TDD work: leaves stepping on each other's files, leaves quietly making design decisions, and leaves receiving tasks too big to finish coherently. But the cascade is only as good as its inputs — if the spec, contract, and umbrella that `/swarm-spawn` consumes were themselves silently invented, the audit chain has nothing real to anchor against.

`/swarm` is the skill that produces those inputs *with the user in the loop at every design decision*. The user is the source of truth. The skill is the procedure for translating user intent into design artifacts without slipping in silent picks along the way. The `.UNSTATED.md` log is the forced surface area for any pick the procedure could not trace to the user — every entry resolved before hand-off means every design decision in the spec, contract, and umbrella is either user-approved or explicitly accepted as a flagged assumption that `/swarm-spawn`'s downstream sweep will see.

Four commands, three safety nets, one cascade. `/swarm` is the entry point.
