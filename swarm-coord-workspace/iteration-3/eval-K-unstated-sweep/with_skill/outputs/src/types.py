"""Type contract for link_extractor.

Minimal symbols only. Bodies are sentinels — actual behavior lives in leaf
impls downstream. Every symbol cites the spec line it encodes; anything
not directly traceable is in specs/link_extractor.UNSTATED.md.
"""

from __future__ import annotations


# encodes spec.md Inputs (URL string) and Outputs (the links found),
# plus Acceptance criteria 1-3 (fetch, parse, return links).
def extract_links(url: str) -> list[str]:
    """Fetch the webpage at `url`, parse it, and return the links found.

    [source: user-stmt-4, user-stmt-5, user-stmt-6]
    """
    raise NotImplementedError
