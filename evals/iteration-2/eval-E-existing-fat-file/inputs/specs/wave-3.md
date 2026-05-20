# Wave-3 Spec: sync_ops emission hardening

## Overview
Harden the three emission behaviors in `sync_ops.py` with explicit unit tests
and tighter validation. Currently there are no dedicated unit tests per op kind.

## Acceptance criteria

### AC1 — Upsert emission
- `emit_ops()` produces one `upsert_contact` op per enrolled contact.
- Never-enrolled contacts produce zero ops (applies to all op kinds).
- Upsert payload contains `email`, `firstName`, `lastName`; `phone` is included only when non-None.

### AC2 — Tag emission
- `emit_ops()` produces `apply_tag` for action="apply" and `remove_tag` for action="remove".
- Unknown tag action raises `ValueError`.
- Tag name is passed through to payload unchanged.

### AC3 — Custom field emission
- `emit_ops()` produces `set_custom_field` for non-empty field values.
- Empty `field_value` produces zero ops for that field row.
- Payload contains `key` and `value` fields.

## Module layout (existing)
All logic lives in `src/myproj/sync_ops.py`. This file is the impl target for all three ACs.

## Out of scope
- `validate_ops()` and `order_ops()` behavior (covered in wave-4).
- `batch_emit()` integration (covered in wave-4).
- Any GHL API calls (pipeline handles those).
