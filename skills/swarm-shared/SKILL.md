---
name: swarm-shared
description: Shared references, scripts, and templates used by /swarm, /swarm-spawn, /swarm-review, and /swarm-merge. Not directly invocable. Do not call this skill — it exists only so the installer copies its references/, scripts/, and templates/ directories into ~/.claude/skills/swarm-shared/, where the four command skills resolve them by absolute path.
---

# swarm-shared

This is a **support skill**, not an invocable one. It carries the shared assets the four command skills (`/swarm`, `/swarm-spawn`, `/swarm-review`, `/swarm-merge`) reference by absolute path:

- `references/playbook.md` — theory and rationale behind the cascade
- `references/brief-template.md` — canonical leaf brief shape
- `references/config.md` — config file reference
- `references/evaluation-rubric.md` — review scoring rubric
- `scripts/check_invariants.py` — invariant audit helper
- `templates/` — config templates

If you reached this file by reading it directly: nothing to do here. Invoke `/swarm`, `/swarm-spawn`, `/swarm-review`, or `/swarm-merge` instead.
