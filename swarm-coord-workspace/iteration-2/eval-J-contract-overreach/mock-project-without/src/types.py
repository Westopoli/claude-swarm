"""Type / interface contract for the URL shortener.

This file defines the minimum public surface required for the umbrella
definition-of-done to be expressible. Implementations live elsewhere.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


# --- Type aliases -----------------------------------------------------------

LongURL = str
Slug = str


# --- Exceptions -------------------------------------------------------------

class SlugNotFoundError(KeyError):
    """Raised when `lookup` is called with a slug that has no mapping."""


class CollisionError(RuntimeError):
    """Raised when slug generation cannot find a free slug after retries."""


# --- Core protocol ----------------------------------------------------------

@runtime_checkable
class Shortener(Protocol):
    """In-process URL shortener contract."""

    def shorten(self, long_url: LongURL) -> Slug:
        """Store `long_url` and return a freshly minted slug."""
        ...

    def lookup(self, slug: Slug) -> LongURL:
        """Return the long URL previously stored for `slug`.

        Raises:
            SlugNotFoundError: if `slug` has no mapping.
        """
        ...


# --- HTTP handler contract --------------------------------------------------

class RedirectResponse(Protocol):
    """Minimal response shape the redirect handler must return."""

    status_code: int
    headers: dict[str, str]


def redirect_handler(slug: Slug, shortener: Shortener) -> RedirectResponse:
    """Resolve `slug` via `shortener.lookup` and return a 302 response.

    Returns:
        A response with `status_code == 302` and
        `headers["Location"] == shortener.lookup(slug)`.
        On `SlugNotFoundError`, returns a response with `status_code == 404`.

    NOTE: This is a contract stub. The implementation lives in the impl module.
    """
    raise NotImplementedError
