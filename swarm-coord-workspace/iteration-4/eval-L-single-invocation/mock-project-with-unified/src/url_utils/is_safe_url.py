"""leaf-02 impl — is_safe_url. See specs/url_utils.md::AC-2 (spec_lines 21-30)."""
from urllib.parse import urlsplit

import url_utils.types as _types


def is_safe_url(url: str, allowed_hosts: list[str]) -> bool:
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    scheme = parts.scheme.lower()
    host = parts.netloc.lower()
    if not scheme or not host:
        return False
    allowed_lower = {h.lower() for h in allowed_hosts}
    return host in allowed_lower


# Rebind the contract symbol so `from url_utils.types import is_safe_url`
# resolves to this concrete impl after this module is imported.
_types.is_safe_url = is_safe_url
