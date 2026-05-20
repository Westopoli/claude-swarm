# TDD Cascade — Playbook

Condensed theory shared by the `swarm`, `swarm-review`, and `swarm-merge` skills.

The full project-resident version lives at `<project_root>/tdd-parallel-agents.md` (or wherever the project keeps its playbook). This file is the skill's portable summary; if a project ships its own playbook, that one wins on policy questions, and these skills should defer to it.

---

## Core Principle

The spec is the source of truth. Tests encode the spec as executable assertions. Implementation exists only to make tests pass. Nothing is built without a failing test. Nothing is tested without a reviewed spec.

---

## The Cascade

Every decomposition produces exactly four layers, in this order:

```
Spec (in spec_dir)
  ↓ reviewed and locked by human
Shared type contract (type_contract_path)
  ↓ written by parent, locked before decomposition
Umbrella test
  ↓ written by parent, must fail (RED), encodes all acceptance criteria
Decomposition into leaf tasks (briefs_dir)
  ↓ parent slices, assigns, never touches again until merge
```

If the project's playbook adds a gate (e.g., an extra compliance check between spec and type contract, configured via `[gates].extra_spec_gate_cmds`), respect it. The cascade above is the minimum.

---

## The Three Invariants

These are the structural rules a leaf assignment must satisfy. Every recurring failure mode in parallel-agent TDD work reduces to violating one of them. The `/swarm-review` audit checks all three before any leaf may be spawned.

### 1. File-ownership non-overlap

Every file in the source and test directories has **exactly one owner** at any given time.

- Parent owns: specs, shared type contract, test fixtures, umbrella test, integration tests, dependency config.
- Each leaf owns: one test file + one impl file.
- No file may appear in two briefs.
- No brief may name a parent-owned file.

The graphify (or fallback dependency map) must confirm non-overlap **before** assignment. If the map shows a planned coupling between two slices, restructure the slices until each is isolated.

### 2. No design decisions at the leaf

A leaf agent translates spec assertions into code. It does not choose API shapes, invent type names, pick libraries, decide naming, or resolve ambiguity. If the test references a type, that type must already exist in the locked shared contract. If anything is unclear, the leaf stops and escalates.

In a brief, design-decision risk shows up as:
- Verbs like *decide*, *choose*, *design*, *determine*, *figure out*, *resolve*.
- A spec line range that is vague or empty.
- A type import from a path not on the contract allowlist.
- An invitation to "use your judgment" or "as appropriate".

These are caught at audit time, not at execution time.

### 3. Sizing — one leaf, one slice

A leaf must be small enough that the agent can finish it in one pass without intermediate decisions. The unit is fixed: **one test file + one impl file.** Concretely:

- Impl line budget (default 200, configurable).
- Test assertion count (default 20, configurable).
- No internal branching across unrelated behaviors.

If the slice exceeds the budget, it is two leaves, not one. The parent re-slices.

---

## Roles

### Parent

Writes the spec; writes the shared type contract; writes the umbrella test (and confirms RED); slices into leaf briefs; merges leaf diffs one at a time; reruns the umbrella after each merge. Never writes impl code.

### Leaf

Receives one assignment: one test file, one impl file, the spec line range it must satisfy, the DO-NOT-EDIT list, and the contract imports it may use. Runs test → confirms RED → writes minimum impl → confirms GREEN → commits → stops. Never creates files. Never edits anything outside its assignment. Never makes design decisions. On ambiguity, stops and reports — does not guess.

---

## Intake interview and the assumption log

Every cascade skill (`/swarm`, `/swarm-review`, `/swarm-merge`) begins with an **intake interview**. The interview lives in the skill's own SKILL.md "Step 0" section. Its purpose: lock the scope of the batch *before* any procedure runs, because every cascade failure in this project's history traced post-mortem to one of the intake questions being silently inferred by the parent agent instead of stated by the user.

**Interactive invocation:** ask the questions, wait for answers, restate scope, confirm.

**Non-interactive invocation** (sub-agent task, CI, automated trigger): proceed without asking, but record every inferred answer in a per-skill assumption log:

| Skill | Log path |
|---|---|
| `/swarm` | `<briefs_dir>/ASSUMPTIONS.md` |
| `/swarm-review` | `<briefs_dir>/REVIEW_ASSUMPTIONS.md` |
| `/swarm-merge` | `<briefs_dir>/leaf-NN.MERGE_ASSUMPTIONS.md` |

Leaf agents follow the same convention: if a leaf had to infer anything, write `<briefs_dir>/leaf-NN.ASSUMPTIONS.md`.

After all leaves report green and before any `/swarm-merge` runs, the parent runs the **assumption-sweep** (procedure in `/swarm`'s SKILL.md). The sweep reads every log, classifies entries against the spec, the strategy doc, and the type contract, and surfaces drift with a damage assessment and a patch suggestion. The user makes the call on patch vs. redo. Default bias: patch — redo costs an afternoon, a patch usually costs minutes.

The reason this is a written convention rather than a free-form check: an LLM auditing its own inferences in the same turn rarely catches them. A separate sweep, against persisted logs, with explicit categories (contradicts-spec / contradicts-bible / cross-leaf / fabricated / compounded), forces structured re-examination.

---

## Prep steps and cross-sprint seam stability

The cascade works on existing projects, not just green-field ones. Two patterns emerge specifically on mature codebases.

### Prep steps

A **prep step** is a parent-owned architectural commit that happens *before* decomposition — not a leaf brief, not a code-writing task. It exists when reslicing alone cannot resolve a fat-file collision: one existing file covers multiple ACs that must become separate leaves, and sequential waves would cost too much parallelism.

Prep step protocol:
1. Parent identifies the file and the split seam (e.g., one function per AC, one sub-file per op kind).
2. Parent commits the refactor. No new behavior — only structural split.
3. Parent runs the umbrella. Must be green before and green after. If it regresses, the split introduced a bug; fix before proceeding.
4. Parent re-emits briefs against the new sub-files. Each sub-file maps cleanly to one leaf.

The prep step is the parent's move, not the leaf's. No leaf may restructure a file it didn't own before — that is a design decision the cascade explicitly forbids at the leaf layer.

### Seam-axis commitment

The split seam chosen in a prep step (by op kind, by strategy, by module boundary, by contact type) is an architectural commitment. Changing seams later costs a re-restructuring sprint. Before committing, ask:
- Is this axis stable for the next 2–3 sprints?
- Does the axis map to a stable dimension of the spec (e.g., the bible's strategy taxonomy) rather than to the current wave's AC list?
- Will new features add new slices along this axis, or cross-cut it?

Record the seam-axis decision in `decisions.md` with an explicit "review at sprint N" clause. That makes future re-seaming a planned event, not a surprise.

### When not to do a prep step

If sequential waves cost only 1–2 merges of serialization, that is cheaper than a prep-step split. Reserve prep steps for cases where the serialization cost is high (many sequential leaves on the same file over multiple waves) or where the fat file is a recurrence risk (every new sprint hits the same collision).

### Long-term accumulation risk

Many sub-files solve the leaf-isolation problem but introduce new ones at scale: a thin dispatcher gains coordination logic and grows fat; cross-cutting concerns (shared SQL views, shared helpers) must live somewhere and become new parent-owned surfaces; schema rename touches N files instead of 1. These are not reasons to avoid prep steps — they are reasons to commit the seam axis carefully and enforce the "dispatcher stays mechanical" rule in `decisions.md`.

---

## Why the cascade exists

It is the only known way to run many AI agents in parallel without one stepping on another's work, without any of them silently making architectural decisions, and without any of them quietly producing more code than they can keep coherent. The three invariants are not stylistic — they are the structural guarantees that make parallel decomposition safe. Skip one and you re-introduce the failure mode it was preventing.
