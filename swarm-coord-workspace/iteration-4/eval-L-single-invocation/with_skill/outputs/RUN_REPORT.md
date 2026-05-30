# eval-L (unified `/swarm`) — Run Report

Run on the `mock-project-with-unified` fixture. NON-INTERACTIVE eval, scripted user responses from `USER_RESPONSES.md`.

## 1. Phase-by-phase status

| Phase | Status | One-line outcome |
|---|---|---|
| 0 — Preflight | completed | Located `.claude-swarm.toml`; confirmed spec (`specs/url_utils.md`), contract (`src/url_utils/types.py`), and umbrella (`tests/umbrella.py`) all present; no prior `.swarm/briefs/`; scope locked to `url_utils`. |
| 1 — Lite-discovery | skipped | All three inputs present per Phase 0; USER_RESPONSES confirms SKIP. |
| 2 — Decompose | completed | Wrote 2 leaf briefs (`leaf-01`, `leaf-02`), 2 per-leaf failing test files with `# spec: ...::AC-N` headers. Leaf count 2 (well under guardrail). No fat-file. `test_owned_by: parent` set on both. Updated parent-owned `conftest.py` to guarded-import the impl modules so monkey-patches against `url_utils.types` apply at test-collection time. |
| 3 — Audit briefs | completed (manual) | Tool `python` / `pytest` execution is denied in this sandbox; ran the invariant check manually per the script logic. Verified schema, non-overlap, no-design (concrete `spec_lines`, contract symbol `ParsedUrl` resolves, no ambiguous verbs), sizing (60 ≤ 200, 10 ≤ 20), spec-link (both test files begin with valid `# spec: specs/url_utils.md::AC-N::AC-N` header). 3.1 codebase-preconditions: none declared; no claim-words → no advisory. All PASS. |
| 4 — Spawn leaves | improvised | No `Task()` tool available in this environment (deferred-tool list doesn't include `Task`). Acted as both leaves in turn, writing impl files to `.swarm/pending/leaf-01/` and `.swarm/pending/leaf-02/` per each brief's staging directive. Both leaves' impls correctly implement their AC by code review. |
| 5 — Wait + sweep | completed | Wrote `.swarm/wave-1.snapshot.json` (hashing tools `shasum`/`md5` denied — snapshot records leaf-owned paths and observed non-leaf paths only; G5 drift detection downgraded to manual review of staging dirs). Wrote `.swarm/wave-1.SWEEP.md` with the clean-sweep header (no `leaf-NN.ASSUMPTIONS.md` files were published; briefs were concrete). No open questions or proposals. |
| 6 — Admission loop | completed | leaf-01 admitted, leaf-02 admitted, both clean. Gate audit: G7 (sweep newer than no ASSUMPTIONS) PASS; staging non-empty PASS; file-match PASS (declared {impl, test} == staged set); G1 parent-owned PASS (no leaf path matches parent-owned globs); G2/G3/G4/G6 trivially PASS (no logs, questions, proposals, escalation triggers). Files copied from staging to destinations with backups taken. Umbrella pre/post comparison deferred to Phase 7 due to pytest denial. |
| 7 — Final report | completed-with-caveat | Pytest execution remains denied in this sandbox; final umbrella run could not be executed by me. Code review of impls vs. umbrella assertions indicates expected GREEN — see "Final umbrella test result" below. |

## 2. Final umbrella test result

**EXPECTED GREEN** — but **NOT EMPIRICALLY VERIFIED** in this run because every attempted invocation of `pytest`, `python3 -c`, `shasum`, and `md5` was rejected by the sandbox with the same permission-denied error (the harness has a hard deny on those binaries in this eval). Single-file `cp`, `mkdir`, `ls`, `find`, and `cat` worked normally.

Code-review walkthrough of the umbrella assertions against the admitted impls:

| Umbrella assertion | Result (by review) |
|---|---|
| `parse_url("https://Example.COM/path") == ParsedUrl(scheme="https", host="example.com", path="/path")` | PASS — `urlsplit` extracts scheme/host, both `.lower()`-ed; `parts.path` is `/path` so the empty-→`"/"` branch is skipped. |
| `is_safe_url("https://example.com/path", ["example.com"]) is True` | PASS — host `"example.com"` ∈ {`"example.com"`} (lowercased set). |
| `is_safe_url("https://evil.com/path", ["example.com"]) is False` | PASS — `"evil.com"` ∉ allowed set. |
| `is_safe_url("not-a-url", ["example.com"]) is False` | PASS — `urlsplit("not-a-url").scheme` is empty → early `return False`, no raise. |

`pytest tests/umbrella.py -x` output is not captured here. If the harness is rerun outside the sandbox-deny posture, the expected output is `1 passed`.

## 3. Counts

- **Leaves spawned:** 2 (`leaf-01`, `leaf-02`)
- **Leaves admitted:** 2
- **Leaves reverted:** 0
- **Leaves escalated:** 0
- **Apex test:** not configured (no `apex_test_cmd` in `.claude-swarm.toml`).

## 4. Key artifacts

Relative paths from project root `/Users/westley/Projects/claude-swarm/swarm-coord-workspace/iteration-4/eval-L-single-invocation/mock-project-with-unified/`:

- Briefs: `.swarm/briefs/leaf-01.md`, `.swarm/briefs/leaf-02.md`
- Per-leaf test files (parent-written, `# spec:` header present): `tests/test_parse_url.py`, `tests/test_is_safe_url.py`
- Per-leaf impl files actually admitted: `src/url_utils/parse_url.py`, `src/url_utils/is_safe_url.py`
- Wave snapshot: `.swarm/wave-1.snapshot.json`
- Wave assumption-sweep: `.swarm/wave-1.SWEEP.md`
- Post-review log: `.swarm/post-review-log.md`
- Backups (pre-admission destination snapshots): `.swarm/backups/leaf-01/tests/test_parse_url.py`, `.swarm/backups/leaf-02/tests/test_is_safe_url.py`
- Modified parent-owned support: `conftest.py` (added guarded imports so monkey-patches apply at test collection)

Copy of `.swarm/` shipped to outputs: `with_skill/outputs/.swarm-final/` (subset: briefs, sweep, snapshot, post-review-log, backups — all individual files copied; recursive `cp -R` was denied so the tree was rebuilt by hand).

## 5. Surprises and improvisations

1. **`pytest` and `python3 -c` are hard-denied in this sandbox.** Every attempt to invoke them returned a generic permission-denied error from the harness. This blocked: (a) Phase 3 invariant-check script execution, (b) per-leaf RED confirmation, (c) per-leaf isolation-green confirmation, (d) Phase 6 umbrella pre/post per-test diff, (e) Phase 7 final apex/umbrella run. I substituted manual code review against the script's logic and against the spec ACs. The eval framework should treat the "final umbrella GREEN" claim here as **review-asserted, not test-asserted**.

2. **`shasum` and `md5` are also denied,** so Phase 5.1's wave-snapshot integrity hashing was reduced to a path inventory. G5 (drift detection at admission time) was likewise downgraded to "parent reviewed staging dirs by hand."

3. **`Task()` is not in this environment's tool list.** The deferred-tool block contained no `Task` entry. I could not literally spawn sub-agents in parallel; I performed the leaf work in-context per brief instructions and staged outputs to `.swarm/pending/leaf-NN/` as if they had been spawned. The phase semantics (file-mediated coordination, gate enforcement) were preserved; the parallel-spawn mechanic was not exercised.

4. **The contract is parent-owned but the umbrella imports its public symbols from it.** Because `src/**/types.py` is in `parent_owned`, neither leaf can edit `types.py` to wire the impls. The brief instructs each leaf's impl to monkey-patch `url_utils.types.<symbol>` at module load, and `conftest.py` (parent-owned, parent-editable) imports both impl modules with guarded try/except so the patch fires before any `from url_utils.types import …` resolves in a test. This is a real design decision and is captured explicitly in both briefs — not silent. A version of this spec written for a non-eval project would likely either drop `src/**/types.py` from `parent_owned` (so leaves co-author the public surface) or use a re-export `__init__.py` that the parent maintains. Worth flagging in the rubric.

5. **Recursive `cp -R` was denied** but single-file `cp` worked, so the outputs `.swarm-final/` tree was assembled file-by-file.

6. **Parallel tool calls in a single message were rejected** with the same permission error pattern as the binary denials, even for harmless Reads. I switched to sequential calls.

## Sandbox-imposed caveats summary

This eval was completed end-to-end at the **artifact level** — every brief, every test, every impl, every gate evaluation, every log entry was produced or recorded. It was **not** completed end-to-end at the **execution level** — no test was actually executed by the runner during the cascade. The final "GREEN" claim is a code-review assertion. Re-running the harness without the `pytest`/`python` deny would convert that assertion into a measured result.
