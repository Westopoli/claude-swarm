"""leaf-01 impl — parse_url. See specs/url_utils.md::AC-1 (spec_lines 9-19)."""
from urllib.parse import urlsplit

import url_utils.types as _types
from url_utils.types import ParsedUrl


def parse_url(url: str) -> ParsedUrl:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = parts.netloc.lower()
    if not scheme or not host:
        raise ValueError(f"URL missing scheme or host: {url!r}")
    path = parts.path if parts.path else "/"
    return ParsedUrl(scheme=scheme, host=host, path=path)


# Rebind the contract symbol so `from url_utils.types import parse_url`
# resolves to this concrete impl after this module is imported (parent
# conftest.py performs the import at test-collection time).
_types.parse_url = parse_url
