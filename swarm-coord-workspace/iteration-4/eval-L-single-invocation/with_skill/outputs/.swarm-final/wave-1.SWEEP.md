# Wave 1 assumption-sweep

Assumption-sweep clean. 0 assumptions reviewed (briefs were concrete; no leaf published an ASSUMPTIONS file).

## Notes

- Leaf-01 and leaf-02 received fully-specified briefs (concrete spec_lines, concrete contract_imports, no ambiguous verbs). No inference required.
- The known design hook (impl modules monkey-patch `url_utils.types` because the contract is parent-owned and cannot be edited by leaves) is explicit in both briefs — not an unstated assumption.
- No `.swarm/questions/` entries published.
- No `.swarm/proposals/` entries published.

## Cross-leaf coherence check

- Both impl modules rebind their symbol on the same module (`url_utils.types`). Order of import does not matter (each rebinds a different attribute).
- Neither leaf imports the other's module (leaf-02 brief explicitly forbids cross-leaf import; uses `urllib.parse` directly).
- Wave is internally coherent.
