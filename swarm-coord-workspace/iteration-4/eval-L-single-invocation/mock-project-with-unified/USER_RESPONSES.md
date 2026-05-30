# Scripted user responses — eval-L (unified `/swarm`)

NON-INTERACTIVE mode. Real user not present. This file is canonical user-response transcript. When skill prompts a question, match below. If no match: log unanswered, proceed under skill's own non-blocking defaults — do NOT hang waiting for user.

Project state on entry:
- `.claude-swarm.toml` present
- `specs/url_utils.md` present (with Bible Compliance footer)
- `src/url_utils/types.py` present (contract: stubs raising NotImplementedError)
- `tests/umbrella.py` present and RED

Phase 1 should fully skip (all three inputs present).

---

## Q (any Phase 0 ambiguity — spec name, dir, etc.)
A: `url_utils` is the spec name. Proceed.

## Q (Phase 1 — anything)
A: SKIP — all three artifacts already on disk.

## Q (Phase 2.2 task-size confirm — only fires at 13–16 leaves)
A: This spec produces 2 leaves; question should not fire.

## Q (Phase 2 fat-file warning)
A: No fat files in this project. Should not fire.

## Q (Phase 3 audit — invariants)
A: Trust the script output. If FAIL, fix the brief in place and re-run; do not escalate.

## Q (Phase 5 sweep — any drift flagged)
A: Patch in place; do not redo. If the patch is non-trivial, accept-as-flagged and continue.

## Q (Phase 6 per-leaf gate failure)
A: If a leaf hits an admission gate failure, revert that leaf, log to `post-review-log.md`, continue with the rest.

## Q (anything else not covered)
A: Proceed under the skill's own default — non-blocking advisories pass, blocking checks fail loudly.
