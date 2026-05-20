# Merge Evaluation Transcript — eval-D-cascade-merge (without_skill baseline)

Date: 2026-05-20  
Evaluator: Claude Sonnet 4.6 (no skill)

---

## Evaluation Criteria

For each merge, I check three things:

1. **Scope match** — Do the new passes correspond to what the leaf's files are responsible for?
2. **No regressions** — Do any previously-passing umbrella assertions now fail?
3. **Net positive** — Does the pass count go up (or at least stay the same)?

A single regression is enough to REVERT, regardless of how many new passes were gained. The TDD cascade invariant is that merging a leaf must never break any assertion that was green before.

---

## merge-1

**Files:** `src/myproj/filters/predicate.py`, `tests/unit/test_filter_predicate.py`

**Before:** 0/8 passing (all 8 failing — this is the very first leaf merge, starting from red)

**After:** 2/8 passing
- PASS: filter predicate eq
- PASS: filter predicate gt

**Analysis:**
- The two new passes directly match the leaf's scope (predicate.py implements eq and gt filter logic).
- No previously-passing tests existed, so regression is impossible.
- Pass count: 0 → 2. Net positive.

**Verdict: MERGE**

---

## merge-2

**Files:** `src/myproj/rollup/groupby.py`, `tests/unit/test_rollup_groupby.py`

**Before:** 2/8 passing (filter predicate eq, filter predicate gt)

**After:** 4/8 passing
- PASS: filter predicate eq (retained)
- PASS: filter predicate gt (retained)
- PASS: rollup groupby returns dict (NEW)
- PASS: types module loads (NEW)

**Analysis:**
- The primary new pass (rollup groupby returns dict) matches the leaf's scope directly.
- "types module loads" passing as a side effect is expected — the rollup module completing its import chain likely satisfied the types loading check that was previously blocked by missing imports.
- No regressions: both prior passes retained.
- Pass count: 2 → 4. Net positive.

**Verdict: MERGE**

---

## merge-3

**Files:** `src/myproj/aggregator/window.py`, `tests/unit/test_window_slide.py`

**Before:** 4/8 passing
- PASS: filter predicate eq
- PASS: filter predicate gt
- PASS: rollup groupby returns dict
- PASS: types module loads

**After:** 3/8 passing
- PASS: window slide produces buckets (NEW)
- PASS: rollup groupby returns dict (retained)
- PASS: types module loads (retained)
- FAIL: filter predicate eq (REGRESSION — was passing before)
- FAIL: filter predicate gt (REGRESSION — was passing before)

**Analysis:**
- The leaf gained its target pass (window slide produces buckets). Good.
- However, two previously-passing tests — filter predicate eq and filter predicate gt — are now FAILING.
- This is a clear regression. The window.py implementation broke something in the predicate filter path, likely through a shared import, a namespace collision, a side effect on a shared module, or a monkey-patched fixture.
- Net pass count went DOWN: 4 → 3.
- Under TDD cascade rules, any regression is a hard REVERT. The leaf must be fixed before it can land.

**Verdict: REVERT**

---

## merge-4

**Files:** `src/myproj/aggregator/tumble.py`, `tests/unit/test_window_tumble.py`

**Before:** 4/8 passing
- PASS: filter predicate eq
- PASS: filter predicate gt
- PASS: rollup groupby returns dict
- PASS: types module loads

**After:** 5/8 passing
- PASS: filter predicate eq (retained)
- PASS: filter predicate gt (retained)
- PASS: rollup groupby returns dict (retained)
- PASS: types module loads (retained)
- PASS: window tumble alignment (NEW)

**Analysis:**
- Note: merge-4's BEFORE state is the same as merge-3's BEFORE — these branches are evaluated independently from main, not sequentially. This is correct TDD cascade behavior: each branch was cut from main at the same point.
- The single new pass (window tumble alignment) corresponds exactly to the leaf's scope (tumble.py).
- All 4 prior passes retained. No regressions.
- Pass count: 4 → 5. Net positive.

**Verdict: MERGE**

---

## merge-5

**Files:** `src/myproj/dashboard/view.py`, `tests/unit/test_dashboard_view.py`

**Before:** 5/8 passing
- PASS: filter predicate eq
- PASS: filter predicate gt
- PASS: rollup groupby returns dict
- PASS: types module loads
- PASS: window tumble alignment

**After:** 7/8 passing
- PASS: filter predicate eq (retained)
- PASS: filter predicate gt (retained)
- PASS: rollup groupby returns dict (retained)
- PASS: types module loads (retained)
- PASS: window tumble alignment (retained)
- PASS: dashboard view renders (NEW)
- PASS: aggregator pipeline end-to-end (NEW)
- FAIL: window slide produces buckets (was already failing — not this leaf's responsibility)

**Analysis:**
- The primary new pass (dashboard view renders) matches the leaf's scope directly.
- "aggregator pipeline end-to-end" passing is expected cascade behavior — the pipeline test likely requires a working dashboard view as one of its dependencies, and once view.py lands, the end-to-end path completes.
- All 5 prior passes retained. No regressions.
- The one remaining failure (window slide produces buckets) is the responsibility of the window/slide leaf (merge-3, which we are reverting). It was already failing before this merge.
- Pass count: 5 → 7. Net positive.

**Verdict: MERGE**

---

## Summary Table

| Merge | Files Touched | Before | After | Regressions | Verdict |
|-------|--------------|--------|-------|-------------|---------|
| merge-1 | filters/predicate.py | 0/8 | 2/8 | None | MERGE |
| merge-2 | rollup/groupby.py | 2/8 | 4/8 | None | MERGE |
| merge-3 | aggregator/window.py | 4/8 | 3/8 | 2 (predicate eq, predicate gt) | REVERT |
| merge-4 | aggregator/tumble.py | 4/8 | 5/8 | None | MERGE |
| merge-5 | dashboard/view.py | 5/8 | 7/8 | None | MERGE |

---

## Key Decision Principle Applied

The only REVERT is merge-3. The tell is unambiguous: two tests that were green before the merge are red after. A leaf agent must never break assertions outside its own scope. Whether the cause is a bad import, shared state mutation, or a fixture side effect, the outcome is the same — the branch cannot land until the regression is diagnosed and fixed.

All other merges show monotonic progress: pass count goes up, no previously-green tests turn red, and the new passes correspond to the leaf's declared scope.
