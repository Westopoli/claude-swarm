## Assumptions made during leaf-02

This leaf could not reach GREEN. Escalating to the parent per the brief's
escalation triggers ("Stop and report to the parent if: ... The impl would
need to edit a file in do_not_edit.").

### Hard blockers

- **Missing field on contract type `Session`** — The brief (lines 19-22)
  requires `session.device_id` to be readable as an attribute after
  `register_device(session, device_id)`. The locked type contract
  (`src/types.py`) defines `Session` as a frozen-by-convention dataclass
  with only `user_id` and `last_seen`. There is no `device_id` field, and
  the brief lists `src/types.py` in `do_not_edit`. — source: `src/types.py`
  lines 5-8; brief lines 24-27.

- **Missing `spec.md`** — The brief cites `spec_file: spec.md` lines 60-80
  but no `spec.md` exists at the project root or anywhere in the project
  tree. Without the spec I cannot disambiguate between candidate impl
  shapes (e.g., does the spec permit a wrapper type? does it require
  `session.device_id` to be persistent across processes?). — source:
  `find . -name spec.md` returned no results.

### Inferences I refused to make silently

The following workarounds would each technically produce a passing test,
but each is a design decision that the cascade explicitly forbids at the
leaf layer (playbook invariant #2 — "No design decisions at the leaf").
Documenting them here so the parent can see what was rejected and why:

1. **Edit `src/types.py` to add `device_id`** — Forbidden by `do_not_edit`.
   This is the cleanest fix but belongs to the parent (a type-contract
   change is a parent-owned, human-reviewed step per playbook).

2. **Use `object.__setattr__` / dynamic attribute attachment in
   `register_device`** — Plain `@dataclass` allows attribute assignment,
   so `session.device_id = device_id` would work at runtime, but this
   silently extends the contract surface. Downstream auth code reading
   `session.device_id` would depend on a field that is not declared on
   the type. Rejected as a design decision.

3. **Return a new wrapper type** — Would require either a new file
   (forbidden — "impl would need to create a new file outside impl_file")
   or a new symbol in `src/device_registry.py` that re-shapes the
   contract. Rejected as a design decision.

4. **External registry dict mapping session-id → device-id** —
   Plausible but the brief says "session.device_id" by attribute
   access, not a lookup function. Rejected as contradicting the brief.

### What was staged

- `.swarm/pending/leaf-02/tests/test_device_registry.py` — the RED test
  faithful to the brief's behavioral claim (`session.device_id == "d1"`
  after `register_device`). Confirmed RED. Not green; no impl staged.
- No impl file is staged. `src/device_registry.py` cannot be written
  without one of the rejected design decisions above.

### Recommended parent action

Add `device_id: str | None = None` to `Session` in `src/types.py` as a
parent-owned prep commit (default `None` so existing `Session(user_id,
last_seen)` callsites keep working), then re-issue leaf-02 unchanged.
The impl becomes a one-liner: `session.device_id = device_id`. — source:
playbook "Prep steps" section; brief's "downstream auth checks can look
it up by `session.device_id`" requirement.
