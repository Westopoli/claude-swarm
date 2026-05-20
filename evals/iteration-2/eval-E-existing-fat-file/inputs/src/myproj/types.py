from dataclasses import dataclass
from typing import Optional, List
from typing import Literal

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
    action: str

@dataclass
class CustomFieldRow:
    contact_id: str
    field_key: str
    field_value: str

@dataclass
class SyncOp:
    kind: str
    contact_id: str
    payload: dict

OpKind = Literal["upsert_contact", "apply_tag", "remove_tag", "set_custom_field"]
