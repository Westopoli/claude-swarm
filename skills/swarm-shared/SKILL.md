---
name: swarm-shared
description: Shared references, scripts, and templates used by /manager-mode. Not directly invocable. Do not call this skill — it exists only so the installer copies its references/, scripts/, and templates/ directories into ~/.claude/skills/swarm-shared/, where /manager-mode resolves them by absolute path.
---

# swarm-shared

This is a **support skill**, not an invocable one. It carries the shared assets `/manager-mode` references by absolute path:

- `references/playbook.md` — theory and rationale behind the cascade
- `references/brief-template.md` — canonical leaf brief shape
- `references/config.md` — config file reference
- `references/evaluation-rubric.md` — review scoring rubric
- `scripts/check_invariants.py` — invariant audit helper
- `templates/` — config templates

If you reached this file by reading it directly: nothing to do here. Invoke `/manager-mode` instead.
