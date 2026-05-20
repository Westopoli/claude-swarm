# claude-swarm

> Disciplined parallel-agent TDD for Claude Code. One sprint, many leaves, zero drift.

`claude-swarm` is a Claude Code skill pack that turns a locked spec into a set of parallel sub-agent tasks — without the usual failure modes (overlapping file edits, silent design decisions, oversized leaves, regressions slipping past merge).

It ships three slash commands:

| Command | What it does |
|---|---|
| `/swarm` | Bootstrap a sprint: spec gate → type contract → umbrella RED → emit leaf briefs |
| `/swarm-review` | Audit leaf briefs against three invariants (non-overlap, no design leak, sizing) before any agent spawns |
| `/swarm-merge` | Post-leaf merge protocol: verify the 2-file diff, rerun the umbrella, revert on regression |

Three commands. Three safety nets. One cascade.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/Westopoli/claude-swarm/main/install.sh | bash
```

That copies the skills into `~/.claude/skills/`. Restart Claude Code, then invoke any of:

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

## How a sprint flows

```
spec.md  ──►  /swarm  ──►  briefs/leaf-01.md, leaf-02.md, …
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
                       umbrella turns green
```

1. **`/swarm`** asks you 7-8 intake questions (spec path, wave, expected leaf count, strategy doc, scope, etc.), then locks the cascade config, confirms the umbrella test fails (RED), and emits one brief per leaf to `.swarm/briefs/`.
2. **`/swarm-review`** runs a deterministic script (`check_invariants.py`) over every brief and checks: no two leaves edit the same file, no brief contains ambiguous "decide/design/figure out" language, every brief stays within budget. Any FAIL blocks spawning.
3. You spawn the leaf agents (each agent takes exactly one brief).
4. **`/swarm-merge`** runs after each leaf reports green. It verifies the diff is exactly two files (one test + one impl), reruns the umbrella, and reverts the merge if the umbrella regresses.

## Config

Drop a `.claude-swarm.toml` at your repo root to override defaults. Full schema at [skills/swarm-shared/references/config.md](skills/swarm-shared/references/config.md). Example template lives at [skills/swarm-shared/templates/.claude-swarm.toml.example](skills/swarm-shared/templates/.claude-swarm.toml.example).

Minimum viable config:

```toml
spec_dir          = "specs/"
briefs_dir        = ".swarm/briefs/"
umbrella_test_cmd = "pytest tests/umbrella -x"
type_contract_path = "src/contract.py"
```

## Why this exists

Three failure modes recur in parallel-agent TDD work:

1. **Leaves stepping on each other's files** — two agents edit the same module, last write wins, silent loss of work.
2. **Leaves quietly making design decisions** — an underspecified brief leaves the agent to "decide" how something should work; the resulting design drifts from the strategy doc.
3. **Leaves receiving tasks too big to finish coherently** — one brief covers three acceptance criteria, the agent runs out of context, half the work is half-done.

The cascade structurally prevents all three — but only if the parent agent assigns leaves correctly, the audit catches mistakes before any agent spawns, and the merge protocol catches regressions before they land. That's exactly what these three commands do.

## Reading order

- New here? Run `/swarm` on a small spec and let it walk you through.
- Want the theory? Read [skills/swarm-shared/references/playbook.md](skills/swarm-shared/references/playbook.md).
- Want the brief shape? See [skills/swarm-shared/references/brief-template.md](skills/swarm-shared/references/brief-template.md).
- Want the audit rules? See [skills/swarm-shared/scripts/check_invariants.py](skills/swarm-shared/scripts/check_invariants.py).

## License

MIT.
