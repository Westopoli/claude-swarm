# claude-swarm

> Disciplined parallel-agent TDD for Claude Code. One north-star test, many sub-tasks, zero drift.

![License](https://img.shields.io/badge/license-MIT-blue)
![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-D97757)
![Status](https://img.shields.io/badge/status-v1.1-green)

[Why TDD + AI](#why-tdd-for-ai-agents) • [Before / After](#before--after) • [Benchmarks](#benchmarks) • [What you get](#what-you-get) • [How it works](#how-it-works) • [Install](#install) • [Config](#config)

A Claude Code skill pack that lets you run many AI sub-agents in parallel without the usual failure modes: overlapping file edits, silent design decisions, oversized tasks, regressions slipping past merge.

Three slash commands. A dozen layered gates. One tree-shaped cascade.

| Command | What it does |
|---|---|
| `/swarm` | Plans the work: reads your requirements, writes a single failing umbrella test that defines "done", checks the umbrella for behavioral strength (not source-grep), emits one task description per sub-agent. |
| `/swarm-review` | Audits task descriptions before any sub-agent starts. Blocks on overlap, ambiguous design language, oversize, and unverified codebase-state claims (`verify:` commands on briefs). |
| `/swarm-merge` | Lands each sub-agent's work safely. Runs ten gates per merge (G1–G7 + ASSUMPTIONS + bypass + apex) and reverts if the umbrella regresses. See [Gate reference](#gate-reference). |

---

## Why TDD for AI agents

AI agents fail in three predictable ways:

1. **Silent design.** Underspecified tasks let the agent "decide" how something should work. The choice never surfaces — it just becomes code.
2. **Vibes-pass "done".** Agents declare victory at the first plausible-looking output. You find out it wasn't done in integration. Or in prod.
3. **Parallel agents amplify both.** Five agents drifting in five directions, each "done", none of them composing.

A failing test fixes the root cause. The API is pinned before any code runs — no room to invent a different shape. "Done" becomes a binary, machine-checkable signal. Regressions get loud instead of staying silent. TDD has been the right discipline for 20 years; it's *especially* the right discipline for AI agents, because silent design drift is the failure mode autoregressive models are most prone to.

## The north-star test

Every wave starts with **one failing test** that defines what "done" looks like for the entire batch of work. We call it the **umbrella test** — it's the north star every sub-agent moves toward.

```
                                umbrella test (failing)
                                          │
                   ┌──────────────────────┼──────────────────────┐
                   ▼                      ▼                      ▼
               sub-task 1             sub-task 2             sub-task 3
          (one test + one impl)  (one test + one impl)  (one test + one impl)
                   │                      │                      │
                   └──────────────────────┼──────────────────────┘
                                          ▼
                                umbrella test (passing)
                                          │
                                      wave done
```

Each sub-task is one test file + one impl file. The sub-task is done when its own test passes. The wave is done when the umbrella test passes. No passing umbrella, no merge.

## Before / After

### Without claude-swarm

```
"spawn 5 agents on this"
        │
        ▼
   Agent A ──── edits auth.py
   Agent B ──── also edits auth.py    ← collision, last write wins
   Agent C ──── invents JWT           ← requirements said sessions, silent drift
   Agent D ──── task too big          ← ran out of context, half-stubbed
   Agent E ──── "done!"               ← integration test still failing, nobody noticed
```

### With claude-swarm

```
   /swarm  ──►  sub-task descriptions      (umbrella test failing, locked in)
                  │
                  ▼
             /swarm-review  ──►  PASS / FAIL
                  │ (only on PASS)
                  ▼
       spawn sub-agents in parallel
                  │
                  ▼
       for each green sub-task: /swarm-merge
                  │
                  ▼
            umbrella test passes → wave done
```

## Benchmarks

Paired evals (one with `claude-swarm`, one without), each targeting a specific failure mode. Graded on **mistake prevention**, not pass-rate, tokens, or wall-clock. Methodology: [skills/swarm-shared/references/evaluation-rubric.md](skills/swarm-shared/references/evaluation-rubric.md).

**Core safety suite (A–E):**

| Eval | Failure mode tested | Without skill | With skill |
|---|---|---|---|
| **A** | Fault detection at 15-way fan-out | Both produced output | Caught 2 silent drifts |
| **B** | Skipping the failing-test gate | **Failed silently** | **Blocked correctly** |
| **C** | Requirements vs strategy contradiction | Both halted | Skill kept an audit trail |
| **D** | Silent regression across 5 merges | Both correct | Skill kept a reviewable record |
| **E** | Two sub-tasks targeting same fat file | **Failed silently** | **Blocked correctly** |

**Coordination-pattern suite (F–H):**

| Eval | Failure mode tested | Without skill | With skill |
|---|---|---|---|
| **F** | Sibling-leaf assumption drift | Both adopted the same value (forced by brief) | Channel surfaced via sibling-ASSUMPTIONS read |
| **G** | Leaf resolved a blocked decision by self-inference | **Merge approved despite open question** | **G3 blocked merge** |
| **H** | Leaf workaround instead of proposing a contract change | Blocked via narrative escalation | Blocked via structured `.swarm/proposals/` (auditable) |

- **8/8 evals**: correct verdict with the skill.
- **3/8 evals (B, E, G)**: baseline silently failed a safety property; skill blocked.
- **0 false positives** on `/swarm-review` audit verdicts.
- Coord-pattern suite (F/G/H): old skill 78% ± 38%, new skill 100% ± 0%.

The load-bearing evals are B, E, and G: real time gets lost when those gates get skipped in production work. The skill blocked all three.

## What you get

| Skill | What |
|---|---|
| `/swarm` | Plans the wave: short intake interview, runs your project's gate commands, writes the failing umbrella test, emits one task description per sub-agent. |
| `/swarm-review` | Runs a deterministic audit script. Blocks if any two tasks edit the same file, if any task contains ambiguous design verbs (`decide`, `figure out`, …), or if any task exceeds the size budget. |
| `/swarm-merge` | Lands each sub-agent's work. Staged files must match the brief's declared `impl_files` + `test_files` (one or more of each). Runs ten gates (G1–G7, ASSUMPTIONS, bypass, apex). Reverts if the umbrella regresses. |
| `check_invariants.py` | Standalone audit script — runnable in CI without Claude Code. |
| `playbook.md` | The full theory: why each invariant exists, what failure mode it prevents. |

## How it works

1. **Define "done".** Write one failing test that captures what the wave needs to achieve. Without this, the workflow has nothing to anchor to.
2. **Plan the sub-tasks.** `/swarm` interviews you briefly, then writes one task description per sub-agent. Each task owns one or more impl files + one or more test files, declared in the brief's `impl_files` / `test_files` frontmatter.
3. **Audit before spawning.** `/swarm-review` runs the audit script. Any failure blocks the workflow — you cannot proceed to step 4 with a failing audit.
4. **Spawn sub-agents in parallel.** One agent per task description. They never message each other directly — all coordination is file-mediated and parent-arbitrated (see [Coordination model](#coordination-model) below).
5. **Merge each finished sub-agent.** `/swarm-merge` checks staged files, reruns the umbrella test, reverts on regression.
6. **Sweep assumptions.** When everything's green, the parent sweeps every sub-agent's assumption log for drift. Anything that contradicts the requirements or shared types surfaces as a flagged entry with a suggested patch.

## Coordination model

The cascade is a tree: parent at root, leaves at fringe, no edges between leaves. Direct leaf-to-leaf messaging would turn the cascade into a graph and destroy regression attribution. But leaves do sometimes need to coordinate. Three file-mediated patterns let them — without breaking the tree shape:

| Pattern | What | Where it fires |
|---|---|---|
| **Sibling-ASSUMPTIONS read** | Leaves read (never write) other leaves' `.ASSUMPTIONS.md` before logging their own. Catches drift at leaf-time instead of merge-time. | Leaf brief boilerplate |
| **Question ledger** | Leaf publishes `.swarm/questions/leaf-NN-Q<n>.md` instead of inferring silently. Parent answers asynchronously in `.swarm/answers/`. | `/swarm-merge` **G3** gate enforces resolution |
| **Contract proposals** | Leaf publishes `.swarm/proposals/leaf-NN.md` instead of editing parent-owned files. Parent applies + accepts. | `/swarm-merge` **G4** gate verifies application |

What's intentionally **not** built: direct leaf-to-leaf messaging, shared mutable state, synchronous waits, cross-leaf impl reads from `.swarm/pending/`. Each would re-introduce a failure mode the cascade exists to prevent.

## Gate reference

Every safety net is a numbered gate. Each runs at a specific point in the workflow.

| Gate | What | Skill |
|---|---|---|
| `non-overlap` | No two briefs name the same impl file. | `/swarm-review` |
| `no-design` | No ambiguous verbs in task prose; no symbols outside the locked contract. | `/swarm-review` |
| `sizing` | Impl/test budgets within configured caps. | `/swarm-review` |
| `codebase-preconditions` | `verify:` commands on briefs that claim codebase state pass. | `/swarm-review` |
| `weak-umbrella` heuristic | Umbrella test asserts on *behavior*, not source-grep. | `/swarm` step 4 |
| `G1` parent-owned | No staged file matches `parent_owned` globs. | `/swarm-merge` |
| `G2` ASSUMPTIONS | Inferences are logged, not buried. | `/swarm-merge` |
| `G3` open-question | Every published question has an answer or `unanswered: true` ack. | `/swarm-merge` |
| `G4` contract-proposal | No `pending` proposals; `accepted` proposals are actually applied. | `/swarm-merge` |
| `G5` wave-snapshot integrity | No file outside the leaf's footprint changed since wave start. | `/swarm-merge` |
| `G6` escalation-trigger | Any brief-declared `detect:` command that matches requires a filed escalation. | `/swarm-merge` |
| `G7` wave-sweep | Parent's aggregate assumption-sweep ran before first merge of wave. | `/swarm-merge` |
| `apex-test` | Behavioral integration test passes after all leaves of the queue merge. | `/swarm-merge` queue completion |
| `bypass-detection` | Every prior leaf was gated through `/swarm-merge`; no leaf landed without audit. | `/swarm-merge` |

## Install

Copies the skills into `~/.claude/skills/`. Restart Claude Code, then invoke any of `/swarm`, `/swarm-review`, `/swarm-merge`.

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/Westopoli/claude-swarm/main/install.sh | bash
```

**Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/Westopoli/claude-swarm/main/install.ps1 | iex
```

### Manual install

```bash
# macOS / Linux
git clone https://github.com/Westopoli/claude-swarm
cd claude-swarm
./install.sh
```

```powershell
# Windows
git clone https://github.com/Westopoli/claude-swarm
cd claude-swarm
.\install.ps1
```

### Uninstall

```bash
# macOS / Linux
rm -rf ~/.claude/skills/{swarm,swarm-review,swarm-merge,swarm-shared}
```

```powershell
# Windows
Remove-Item -Recurse -Force $env:USERPROFILE\.claude\skills\swarm*, $env:USERPROFILE\.claude\skills\swarm-shared
```

## Config

Optional. Drop a `.claude-swarm.toml` at your repo root to point claude-swarm at your test command and project layout:

```toml
spec_dir           = "specs/"
briefs_dir         = ".swarm/briefs/"
umbrella_test_cmd  = "pytest tests/umbrella -x"
type_contract_path = "src/contract.py"
```

Without a config file, claude-swarm uses sensible defaults — the only thing you'll *probably* need to set is `umbrella_test_cmd` so it knows how to run your test suite.

**What you can tune (via `.claude-swarm.toml`, never edit the script):**

| Knob | Default | What it controls |
|---|---|---|
| `spec_dir` | `specs/` | Where your requirements docs live |
| `briefs_dir` | `.swarm/briefs/` | Where sub-task descriptions land |
| `type_contract_path` | _(unset)_ | Shared types file all sub-agents import |
| `umbrella_test_cmd` | _(unset)_ | Command that runs the "done" test |
| `parent_owned` | types files, conftest, umbrella tests, integration tests | Files only the parent agent can edit |
| `max_impl_lines` | `200` | Cap on sub-task impl file size |
| `max_test_assertions` | `20` | Cap on sub-task test file size |
| `ambiguous_verbs` | `decide`, `choose`, `design`, `figure out`, … | Banned words in task descriptions |

Full schema at [skills/swarm-shared/references/config.md](skills/swarm-shared/references/config.md).

## License

MIT. Use it, fork it, ship it.
