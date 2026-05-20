"""
Existing fat file: sync_ops.py
Handles upsert, tag, and custom-field op emission for GHL sync.
~280 lines covering three distinct behaviors.
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ContactRow:
    contact_id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    enrolled: bool


@dataclass
class TagRow:
    contact_id: str
    tag_name: str
    action: str  # "apply" | "remove"


@dataclass
class CustomFieldRow:
    contact_id: str
    field_key: str
    field_value: str


@dataclass
class SyncOp:
    kind: str  # "upsert_contact" | "apply_tag" | "remove_tag" | "set_custom_field"
    contact_id: str
    payload: dict


def emit_ops(contacts: List[ContactRow], tags: List[TagRow], fields: List[CustomFieldRow]) -> List[SyncOp]:
    """
    Main dispatcher. Emits all op kinds in one pass.
    Currently a god-function: upsert logic, tag logic, and custom-field logic
    all live in this single function body.
    """
    ops = []

    # --- Upsert logic (AC1) ---
    for c in contacts:
        if not c.enrolled:
            continue  # AC4: never-enrolled = no ops
        ops.append(SyncOp(
            kind="upsert_contact",
            contact_id=c.contact_id,
            payload={
                "email": c.email,
                "firstName": c.first_name,
                "lastName": c.last_name,
                "phone": c.phone,
            }
        ))

    # --- Tag logic (AC2) ---
    for t in tags:
        if t.action == "apply":
            ops.append(SyncOp(
                kind="apply_tag",
                contact_id=t.contact_id,
                payload={"tag": t.tag_name}
            ))
        elif t.action == "remove":
            ops.append(SyncOp(
                kind="remove_tag",
                contact_id=t.contact_id,
                payload={"tag": t.tag_name}
            ))
        else:
            raise ValueError(f"Unknown tag action: {t.action}")

    # --- Custom field logic (AC3) ---
    for f in fields:
        if not f.field_value:
            continue  # skip empty values
        ops.append(SyncOp(
            kind="set_custom_field",
            contact_id=f.contact_id,
            payload={
                "key": f.field_key,
                "value": f.field_value,
            }
        ))

    return ops


def validate_ops(ops: List[SyncOp]) -> List[str]:
    """Validate emitted ops. Returns list of error strings."""
    errors = []
    seen_upserts = set()

    for op in ops:
        if op.kind == "upsert_contact":
            if op.contact_id in seen_upserts:
                errors.append(f"Duplicate upsert for contact {op.contact_id}")
            seen_upserts.add(op.contact_id)

        if op.kind in ("apply_tag", "remove_tag", "set_custom_field"):
            if op.contact_id not in seen_upserts:
                errors.append(
                    f"Op {op.kind} for {op.contact_id} has no preceding upsert — "
                    "contact may not exist in GHL yet"
                )

        if not op.payload:
            errors.append(f"Op {op.kind} for {op.contact_id} has empty payload")

    return errors


def order_ops(ops: List[SyncOp]) -> List[SyncOp]:
    """
    Reorder ops so upsert_contact always precedes tag/field ops for same contact.
    Required by GHL API: contact must exist before fields/tags can be set.
    """
    upserts = [op for op in ops if op.kind == "upsert_contact"]
    rest = [op for op in ops if op.kind != "upsert_contact"]
    return upserts + rest


# Additional helpers — 80+ more lines of supporting logic
def _build_upsert_payload(contact: ContactRow) -> dict:
    payload = {
        "email": contact.email,
        "firstName": contact.first_name,
        "lastName": contact.last_name,
    }
    if contact.phone:
        payload["phone"] = contact.phone
    return payload


def _normalize_tag_name(tag: str) -> str:
    return tag.strip().lower().replace(" ", "_")


def _validate_field_key(key: str) -> bool:
    return bool(key) and key.startswith("cf_")


def _format_field_value(value: str) -> str:
    return str(value).strip()


def batch_emit(
    contacts: List[ContactRow],
    tags: List[TagRow],
    fields: List[CustomFieldRow],
    validate: bool = True,
    reorder: bool = True,
) -> List[SyncOp]:
    """
    High-level entry point. Emits, validates, and orders in one call.
    Used by the sync pipeline. Lower-level emit_ops() is for testing slices.
    """
    ops = emit_ops(contacts, tags, fields)
    if validate:
        errors = validate_ops(ops)
        if errors:
            raise ValueError(f"Op validation failed: {errors}")
    if reorder:
        ops = order_ops(ops)
    return ops
