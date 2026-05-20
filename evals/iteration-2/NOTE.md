# Note on naming

These evals were run before the release rename. In the transcripts, verdict files, and work directories you will see the old skill names:

| Old (in these transcripts) | New (current release) |
|---|---|
| `/tdd-root` | `/swarm` |
| `/tdd-review` | `/swarm-review` |
| `/tdd-merge` | `/swarm-merge` |
| `tdd-cascade-shared/` | `swarm-shared/` |
| `.tdd-cascade.toml` | `.claude-swarm.toml` |
| `TDD_CASCADE_*` env vars | `CLAUDE_SWARM_*` env vars |
| `.tdd/briefs/` | `.swarm/briefs/` |

The skill content, procedure, and invariants did not change between the eval runs and the released version — only the command names and config filenames were renamed for brand consistency at release. We've left the transcripts verbatim rather than retroactively rewriting them, so the evidence is auditable as captured.

For the released-name documentation, see the [top-level README](../../README.md) and [skills/swarm-shared/references/playbook.md](../../skills/swarm-shared/references/playbook.md).
