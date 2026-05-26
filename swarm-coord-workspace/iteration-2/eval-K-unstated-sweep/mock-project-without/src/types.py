"""Type / interface contract for fetch_links.

This module defines the public surface only. Implementation lives elsewhere.
See specs/spec.md for the inferred-decisions table behind these choices.
"""

from __future__ import annotations

from typing import Protocol


class FetchError(Exception):
    """Raised when the page cannot be retrieved.

    Covers: DNS failure, connection refused, TLS error, timeout,
    and any non-2xx HTTP status (including after following redirects).
    """


class ParseError(Exception):
    """Raised when the response body is not parseable HTML.

    Covers: non-HTML Content-Type (e.g. application/pdf, image/*, application/json)
    and malformed bodies that the parser cannot recover from.
    """


class FetchLinks(Protocol):
    """Callable contract for the fetch_links function.

    Parameters
    ----------
    url:
        An absolute http:// or https:// URL.
    timeout:
        Per-request timeout in seconds (connect+read combined). Default 10.0.

    Returns
    -------
    list[str]
        Absolute URLs extracted from <a href="..."> elements in document
        order. Resolved against the final response URL (after redirects).
        Not deduplicated. Excludes empty hrefs, fragment-only hrefs (``#x``),
        and non-http schemes such as ``javascript:`` and ``mailto:``.

    Raises
    ------
    FetchError
        Network failure, timeout, or non-2xx response.
    ParseError
        Response is not parseable HTML.
    """

    def __call__(self, url: str, *, timeout: float = 10.0) -> list[str]: ...


# Concrete signature export for static type checkers / IDEs.
def fetch_links(url: str, *, timeout: float = 10.0) -> list[str]:  # pragma: no cover
    raise NotImplementedError("fetch_links is not implemented yet")
