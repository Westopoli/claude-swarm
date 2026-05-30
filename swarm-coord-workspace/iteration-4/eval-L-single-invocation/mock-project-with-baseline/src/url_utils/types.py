"""Contract: public symbols for url_utils. Impl lives in sibling modules."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedUrl:
    scheme: str
    host: str
    path: str


def parse_url(url: str) -> ParsedUrl:
    from url_utils.parse_url import parse_url as _impl
    return _impl(url)


def is_safe_url(url: str, allowed_hosts: list[str]) -> bool:
    from url_utils.is_safe_url import is_safe_url as _impl
    return _impl(url, allowed_hosts)
