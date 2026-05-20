# Merge Eval D — Non-Interactive Assumptions

Per tdd-merge skill Step 0 (non-interactive path), inferred answers are recorded here.

## Applied to all 5 merges

1. **Which leaf?** Inferred from directory names: merge-1 through merge-5, processed in sequence.
2. **Leaf scope (one-liner)?** Inferred from diff file paths:
   - merge-1: filter predicate impl (src/myproj/filters/predicate.py)
   - merge-2: rollup groupby impl (src/myproj/rollup/groupby.py)
   - merge-3: aggregator window/slide impl (src/myproj/aggregator/window.py)
   - merge-4: aggregator tumble/window alignment impl (src/myproj/aggregator/tumble.py)
   - merge-5: dashboard view impl (src/myproj/dashboard/view.py)
3. **Multi-merge sequence?** Yes — this is a 5-leaf sequential cascade. The umbrella baseline for each merge is the post-previous-merge state (or post-revert state if a merge was reverted). The UMBRELLA_BEFORE files confirm this chaining.
4. **Parent assumption-sweep run?** Unknown — not provided. Proceeding under eval constraints; flag noted.
5. **Expected umbrella delta?** Not provided by user. Deltas inferred from UMBRELLA_BEFORE vs UMBRELLA_AFTER files.

## Notable inference: merge-3 revert effects merge-4 baseline

merge-4's UMBRELLA_BEFORE shows 4 passes (matching merge-3's BEFORE, not AFTER), confirming that merge-3 was reverted before merge-4 ran. This is consistent with correct cascade protocol.
