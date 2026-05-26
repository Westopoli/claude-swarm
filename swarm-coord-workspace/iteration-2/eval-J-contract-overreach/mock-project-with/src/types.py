"""Type contract for url_shortener.

Minimal symbols only. Sentinel bodies — actual behavior is implemented downstream
by leaf agents. The umbrella test imports from this file and asserts on behavior.
"""

from __future__ import annotations

from typing import Tuple


# encodes spec.md acceptance criterion 1 (shorten: long URL -> slug)
def shorten(long_url: str) -> str:
    raise NotImplementedError


# encodes spec.md acceptance criterion 2 (lookup: slug -> original long URL)
def lookup(slug: str) -> str:
    raise NotImplementedError


# encodes spec.md acceptance criterion 3+4 (redirect handler: slug -> 302 with Location header)
# Return shape: (status_code, headers) where headers is a list of (name, value) pairs.
def redirect(slug: str) -> Tuple[int, list[tuple[str, str]]]:
    raise NotImplementedError
