"""Contract: public symbols for url_utils. Impl lives in sibling modules."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedUrl:
    scheme: str
    host: str
    path: str


def parse_url(url: str) -> ParsedUrl:
    raise NotImplementedError("AC-1 — implemented by leaf-1")


def is_safe_url(url: str, allowed_hosts: list[str]) -> bool:
    raise NotImplementedError("AC-2 — implemented by leaf-2")
