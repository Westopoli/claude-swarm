"""leaf-02: AC-2 — is_safe_url implementation. Spec lines 21-30."""
from url_utils.parse_url import parse_url


def is_safe_url(url: str, allowed_hosts: list[str]) -> bool:
    try:
        parsed = parse_url(url)
    except ValueError:
        return False
    allowed_lower = {h.lower() for h in allowed_hosts}
    return parsed.host.lower() in allowed_lower
