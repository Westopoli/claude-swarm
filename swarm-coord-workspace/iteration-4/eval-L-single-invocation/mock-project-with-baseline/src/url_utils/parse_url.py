"""leaf-01: AC-1 — parse_url implementation. Spec lines 9-19."""
from urllib.parse import urlsplit

from url_utils.types import ParsedUrl


def parse_url(url: str) -> ParsedUrl:
    parts = urlsplit(url)
    if not parts.scheme:
        raise ValueError(f"URL is missing a scheme: {url!r}")
    if not parts.netloc:
        # urlsplit("example.com/a") produces scheme="" so the earlier branch
        # catches it; this branch catches inputs like "https:" with no host.
        raise ValueError(f"URL is missing a host: {url!r}")
    scheme = parts.scheme.lower()
    host = parts.netloc.lower()
    path = parts.path if parts.path else "/"
    return ParsedUrl(scheme=scheme, host=host, path=path)
