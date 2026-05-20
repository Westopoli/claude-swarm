# claude-swarm

> Disciplined parallel-agent TDD for Claude Code. One umbrella test, many leaves, zero drift.

![License](https://img.shields.io/badge/license-MIT-blue)
![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-D97757)
![Status](https://img.shields.io/badge/status-v0.1-green)

[Why TDD + AI](#why-tdd-is-the-right-discipline-for-ai-agents) • [The north star test](#the-north-star-test) • [Before / After](#before--after) • [Benchmarks](#benchmarks) • [Install](#install) • [What you get](#what-you-get) • [Evidence](#evidence)

A Claude Code skill pack that turns a locked spec into a set of **parallel sub-agent tasks** without the usual failure modes: overlapping file edits, silent design decisions, oversized leaves, regressions slipping past merge.

Three slash commands. Three safety nets. One cascade.

| Command | What it does |
|---|---|
| `/swarm` | Bootstrap a sprint: spec gate → type contract → umbrella RED → emit leaf briefs |
| `/swarm-review` | Audit briefs against three invariants (non-overlap, no design leak, sizing) before any agent spawns |
| `/swarm-merge` | Post-leaf merge protocol: verify the 2-file diff, rerun the umbrella, revert on regression |

---

## Why TDD is the right discipline for AI agents

Three failure modes dominate AI-agent dev work:

1. **Spec ambiguity → silent design.** An underspecified task lets the agent "decide" how something should work. The choice never surfaces in review — it just becomes code. At scale, half your codebase is undocumented agent design choices.
2. **No machine-checkable signal of "done".** Agents will declare victory at the first plausible-looking output. Without an executable contract, you find out it wasn't done during integration. Or in prod.
3. **Parallel agents amplify both.** Five agents drifting in five directions, each one "done", none of them composing.

**TDD fixes the root cause.** A failing test is an executable spec the agent cannot bullshit its way past:

- The API surface is pinned before any code is written. No room for the agent to invent a different shape.
- "Done" is a green test, not a vibes-pass. The signal is binary, machine-checked, and loud when wrong.
- Refactor stays safe — the same test that defined the contract catches regressions.

This isn't a discovery. TDD has been the right discipline for 20 years. It's *especially* the right discipline for AI agents, because the failure mode TDD prevents — silent design drift — is exactly the failure mode autoregressive LLMs are most prone to.

## The north star test

In `claude-swarm`, every sprint starts with **one umbrella test**: a single failing test that encodes the acceptance criteria for the entire sprint. This is the **north star**.

```
                                       umbrella test (RED)
                                              │
                       ┌──────────────────────┼──────────────────────┐
                       ▼                      ▼                      ▼
                   leaf-01                leaf-02                leaf-03
              (one test + one impl)  (one test + one impl)  (one test + one impl)
                       │                      │                      │
                       └──────────────────────┼──────────────────────┘
                                              ▼
                                       umbrella test (GREEN)
                                              │
                                          sprint done
```

Every leaf is a sub-agent task with **one test file + one impl file**. The leaf is green when its own test passes. The sprint is done when the umbrella test is green. The umbrella is the single source of truth for *done*. No green umbrella, no merge.

The leaves are not "the work" — they're a decomposition of the work *toward the north star*. If a leaf's green doesn't move the umbrella closer to green, the decomposition was wrong, and `/swarm-review` catches it.

## Before / After

### Without claude-swarm — five parallel agents, ad-hoc

```
spec.md  ──►  "spawn 5 agents on this"
                              │
                              ▼
      ┌──── Agent A ──── edits auth.py
      ├──── Agent B ──── also edits auth.py    ← collision, last-write wins
      ├──── Agent C ──── "decides" JWT         ← spec said sessions, silent drift
      ├──── Agent D ──── brief covers 3 ACs    ← runs out of context at AC2
      └──── Agent E ──── done!                 ← umbrella still RED, nobody notices
```

### With claude-swarm

```
spec.md  ──►  /swarm  ──►  briefs/leaf-01.md … leaf-NN.md   (umbrella RED locked in)
                              │
                              ▼
                         /swarm-review  ──►  PASS / FAIL
                              │ (only on PASS)
                              ▼
                   spawn leaf agents in parallel
                              │
                              ▼
                  for each green leaf: /swarm-merge
                              │
                              ▼
                       umbrella GREEN → sprint done
```

`/swarm-review` blocks overlapping file ownership. Briefs forbid design verbs (`decide`, `figure out`). Brief budgets hard-cap line counts so leaves can't get oversized. `/swarm-merge` verifies a 2-file diff and reverts on umbrella regression.

## Benchmarks

We ran five paired evals (one with `claude-swarm`, one without) targeting each of the cascade's claimed safety properties. Methodology and rubric: [skills/swarm-shared/references/evaluation-rubric.md](skills/swarm-shared/references/evaluation-rubric.md). Raw verdicts and transcripts: [evals/iteration-2/](evals/iteration-2/).

We **do not** grade on pass-rate, tokens, or wall-clock. We grade on **mistake prevention** and **plan fidelity at scale** — because that's what fails first in parallel-agent work.

| Eval | What it tests | Without skill | With skill | Outcome |
|---|---|---|---|---|
| **A** — scale, 15 leaves | Fault detection at high fan-out | Both produced output | Skill flagged 2 drifts via assumption-sweep | Skill caught more mistakes |
| **B** — solo-impl prevention | Umbrella-RED gate enforcement | **FAILED** — skipped umbrella gate, emitted briefs anyway | **BLOCKED** — refused to proceed with green umbrella | Skill prevented silent solo-impl |
| **C** — bible drift | Spec-vs-strategy contradiction halt | Both halted correctly | Skill logged void-annotated assumption; baseline did not | Skill provided audit trail |
| **D** — 5-merge cascade | Silent regression detection | Both correct | Skill's assumption logs surfaced merge-3 revert pattern | Skill produced reviewable record |
| **E** — existing fat file | Resolution-path presentation | **FAILED** — emitted overlapping briefs on shared file | **BLOCKED** — presented sequential-waves vs prep-split paths | Skill prevented file-ownership collision |

### Headline numbers

- **5 / 5 evals**: `claude-swarm` produced the correct verdict.
- **2 / 5 evals (B, E)**: the baseline silently *failed* a safety property; the skill **blocked** correctly.
- **4 / 18 inferred assumptions** were flagged by the parent assumption-sweep across all `with_skill` runs — drifts the baseline missed entirely.
- **0 false positives** on `/swarm-review` audit verdicts across the five eval runs.

### What the numbers mean

Two of the five evals (B and E) are the **load-bearing** ones — they target the failure modes that cost real time when they slip past in production work (skipping the umbrella-RED gate; assigning two leaves to the same fat file). The baseline AI agent skipped these gates and proceeded. `claude-swarm` blocked correctly in both cases. **That is the entire value proposition** — at scale, those two skipped gates are how an afternoon turns into a week.

The other three evals (A, C, D) measure the second-order benefit: even when the baseline reaches the right verdict, `claude-swarm` produces structured assumption logs that surface drift the baseline misses entirely. The assumption-sweep at the parent level converted 4 silent inferences into reviewable flags.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Westopoli/claude-swarm/main/install.sh | bash
```

Copies the skills into `~/.claude/skills/`. Restart Claude Code, then invoke any of:

```
/swarm
/swarm-review
/swarm-merge
```

### Manual install

```bash
git clone https://github.com/Westopoli/claude-swarm
cd claude-swarm
./install.sh
```

### Uninstall

```bash
rm -rf ~/.claude/skills/{swarm,swarm-review,swarm-merge,swarm-shared}
```

## What you get

| Skill | What |
|---|---|
| `/swarm` | Sprint bootstrap. 8-question intake, spec gate, umbrella-RED check, fat-file detection, type-contract validation, dependency map, leaf brief emission. |
| `/swarm-review` | Deterministic 3-invariant audit (`check_invariants.py`): no overlapping ownership, no design verbs in briefs, every brief inside budget. Blocks spawning on FAIL. |
| `/swarm-merge` | Post-leaf merge gate. Diff must be exactly 2 files (one test + one impl). Reruns umbrella. Reverts merge if umbrella regresses. |
| `check_invariants.py` | Standalone audit script. Exit 0 = all pass, exit 1 = at least one finding, exit 2 = config error. Runnable in CI. |
| `playbook.md` | The full theory: why the cascade exists, what each invariant prevents, intake interview rationale, parent assumption-sweep procedure. |
| `brief-template.md` | Canonical leaf brief shape. `/swarm-review` will fail any brief that doesn't conform. |

## How it works

1. **Lock the spec.** Pick the spec file, the wave, and the strategy doc. `/swarm` runs the project's gate commands; if any gate fails, the sprint doesn't start.
2. **Write the umbrella test (RED).** A single failing test that encodes the acceptance criteria. Must be RED before any decomposition — if it's green, the cascade has nothing to do.
3. **Decompose into leaf briefs.** One test file + one impl file per brief. Briefs use imperative prose with concrete spec line citations. No design verbs allowed.
4. **Audit before spawning.** `/swarm-review` runs `check_invariants.py` against every brief. Any FAIL blocks spawning. No exceptions.
5. **Spawn agents.** One leaf per agent. Each agent has exactly one brief and the type contract. No cross-leaf coordination needed.
6. **Merge with a guard.** `/swarm-merge` runs per green leaf. Diff must be exactly 2 files. Umbrella reruns. If it regresses, the merge is reverted before next leaf lands.
7. **Sweep assumptions.** After all leaves are green and before declaring sprint done, the parent sweeps every assumption log for drift against the spec, strategy doc, and type contract. Drifts surface as flagged entries with damage assessments and patch suggestions.

## Evidence

- **Full eval bundle:** [evals/iteration-2/](evals/iteration-2/)
- **Evaluation rubric:** [skills/swarm-shared/references/evaluation-rubric.md](skills/swarm-shared/references/evaluation-rubric.md)
- **Per-eval verdicts:** look at `verdict.txt` inside each `eval-X-*/with_skill/outputs/` and `without_skill/outputs/`
- **Per-eval transcripts:** look at `transcript.md` in the same directories
- **Parent assumption-sweep report:** [evals/iteration-2/assumption-sweep-report.md](evals/iteration-2/assumption-sweep-report.md)

> Note: the eval transcripts use the previous skill names (`/tdd-root`, `/tdd-review`, `/tdd-merge`) because they were captured before the release rename. The skill content is unchanged. See [evals/iteration-2/NOTE.md](evals/iteration-2/NOTE.md) for the full mapping.

## Config

Drop a `.claude-swarm.toml` at your repo root to override defaults. Full schema at [skills/swarm-shared/references/config.md](skills/swarm-shared/references/config.md). Example template at [skills/swarm-shared/templates/.claude-swarm.toml.example](skills/swarm-shared/templates/.claude-swarm.toml.example).

Minimum viable config:

```toml
spec_dir          = "specs/"
briefs_dir        = ".swarm/briefs/"
umbrella_test_cmd = "pytest tests/umbrella -x"
type_contract_path = "src/contract.py"
```

## Reading order

- **New here?** Run `/swarm` on a small spec and let it walk you through.
- **Want the theory?** Read [skills/swarm-shared/references/playbook.md](skills/swarm-shared/references/playbook.md).
- **Want the brief shape?** See [skills/swarm-shared/references/brief-template.md](skills/swarm-shared/references/brief-template.md).
- **Want the audit rules?** See [skills/swarm-shared/scripts/check_invariants.py](skills/swarm-shared/scripts/check_invariants.py).
- **Want the evidence?** See [evals/iteration-2/](evals/iteration-2/).

## License

MIT.
