# /swarm-merge dry-run report — leaf-03 (old skill)

Project: `.../eval-G-open-question/mock-project-old`
Skill: `skill-snapshot-old/swarm-merge/SKILL.md`
Mode: dry-run.

## Gate-by-gate

| # | Gate | Result | Evidence |
|---|---|---|---|
| 0.5 | Bypass + audit-log | pass | header valid; only leaf-01 in log |
| 1 | Staging exists | pass | 2 files in `.swarm/pending/leaf-03/` |
| 2 | File-match | pass | staged set = declared set |
| 2 (G1) | Parent-owned | pass | no overlap |
| 3 | Brief sanity | pass | lists present |
| 4 (G2) | ASSUMPTIONS exists | pass | 1 entry |
| 5 | Pre-umbrella | skipped (dry-run) | by inspection: collection error pre, would pass post |
| 6 | Post-umbrella | skipped (dry-run) | by inspection: +1 |
| 6 (G7) | Acceptance | skipped | no `## Acceptance` block |
| 6.5 | Assumption sweep | pass | no sibling ASSUMPTIONS exists to contradict |
| 7 | Regression | pass | empty |
| 7 | Delta | pass | +1 matches inferred expected |
| 8 | Finalise / graphify | skipped | dry-run / graphify_cmd not configured |

## Final decision

**APPROVE** — clean.

## Surfaced concern (not gated by this skill version)

`.swarm/questions/leaf-03-Q1.md` is **open**. The leaf resolved a parent-directed question by self-inference. Old skill never reads `.swarm/questions/`. Skill approves despite open question. This is the gap the eval-G scenario is designed to expose.
