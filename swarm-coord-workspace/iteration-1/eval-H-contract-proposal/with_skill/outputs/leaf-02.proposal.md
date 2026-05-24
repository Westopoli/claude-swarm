---
leaf_id: leaf-02
target_file: src/types.py
status: open
---

## Proposed change

Add a `device_id` field to the `Session` dataclass in `src/types.py`.

Unified diff:

```diff
--- a/src/types.py
+++ b/src/types.py
@@ -1,8 +1,9 @@
 """Parent-owned types. Do not edit from leaf agents."""
 from dataclasses import dataclass
 
 
 @dataclass
 class Session:
     user_id: str
     last_seen: int
+    device_id: str | None = None
```

The field is added with a default of `None` so existing call sites that
construct `Session(user_id=..., last_seen=...)` continue to type-check and
run without modification. `register_device(session, device_id)` will set
this attribute on the passed `Session` instance.

## Why it is needed

Spec lines 60-80 (cited in the brief) require that a `Session` carry its
bound device identifier so downstream auth checks can look it up via
`session.device_id`. The brief's task is to implement
`register_device(session, device_id)` such that `session.device_id` is
readable after the call.

The current `Session` dataclass in `src/types.py` defines only `user_id`
and `last_seen`. There is no `device_id` field. Without this field:

- Writing to `session.device_id` on a frozen-shape `@dataclass` instance
  raises `AttributeError` or `FrozenInstanceError` depending on dataclass
  options, and at minimum violates the type contract.
- The test for leaf-02 cannot assert `session.device_id == <expected>`
  against a real `Session` because the attribute does not exist on the
  contract type.
- Working around with `setattr`, a subclass, or a parallel local type
  would be silent drift from the parent-owned contract — explicitly
  forbidden by both the brief's contract-proposal protocol section and
  the cascade's "no design decisions at the leaf" invariant.

`src/types.py` is listed in `do_not_edit` for this brief, so the leaf
cannot apply the change itself. The proposal protocol is the only
sanctioned path.

## Suggested name / shape

- Field name: `device_id`
- Type: `str | None`
- Default: `None`

Rationale: `device_id` is the exact attribute name the brief specifies
(`session.device_id`). `str` matches the natural shape of an identifier
and is consistent with `user_id: str`. Making it `Optional` with default
`None` preserves backward compatibility for any existing construction
sites that do not yet pass a device identifier — `register_device` is
the call that populates it.

The parent may override (e.g., make it required, use a different type
such as `DeviceId = NewType("DeviceId", str)`, or change the default).
