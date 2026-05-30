# Wave-1 parent assumption-sweep

## Summary
- Total assumptions logged across leaves: 0 (neither leaf wrote a `leaf-NN.ASSUMPTIONS.md` — briefs were concrete enough that no inference was needed beyond the spec).
- Flagged: 0
- Unflagged: 0

## Cross-leaf consistency check
- Both leaves agree the `host` field carries the lowercased host string and that `parse_url` raises `ValueError` on missing scheme. No cross-leaf contradiction.
- Both leaves filed contract proposals targeting `src/url_utils/types.py`: leaf-01 for `parse_url`, leaf-02 for `is_safe_url`. Targets are disjoint (different function bodies in the same file); no proposal conflicts.

## Verdict

Assumption-sweep clean. 0 assumptions reviewed, none drift. Proceed to /swarm-post-review for each leaf.
