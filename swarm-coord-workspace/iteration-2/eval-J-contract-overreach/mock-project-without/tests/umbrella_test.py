"""Umbrella test — pins the definition-of-done for the URL shortener.

This test is intentionally failing until the implementation exists.
It expresses exactly the three "done" assertions from the spec:

  1. shorten() returns a slug.
  2. lookup() on that slug returns the original URL.
  3. The redirect handler returns 302 with Location == original URL.
"""

from __future__ import annotations

import pytest


def test_umbrella_shorten_lookup_redirect():
    # Import lazily so collection still succeeds before impl exists.
    from src.shortener import InMemoryShortener  # type: ignore[import-not-found]
    from src.types import redirect_handler

    shortener = InMemoryShortener()
    long_url = "https://example.com/some/very/long/path?with=query"

    # (1) shorten returns a non-empty slug
    slug = shortener.shorten(long_url)
    assert isinstance(slug, str) and slug, "shorten must return a non-empty slug"

    # (2) lookup round-trips
    assert shortener.lookup(slug) == long_url, "lookup must return the original URL"

    # (3) redirect handler returns 302 with correct Location
    response = redirect_handler(slug, shortener)
    assert response.status_code == 302, "redirect must be HTTP 302"
    assert response.headers.get("Location") == long_url, (
        "redirect Location header must equal the original URL"
    )


def test_umbrella_lookup_miss_raises():
    """Inferred behavior (flagged in spec): unknown slug raises SlugNotFoundError."""
    from src.shortener import InMemoryShortener  # type: ignore[import-not-found]
    from src.types import SlugNotFoundError

    shortener = InMemoryShortener()
    with pytest.raises(SlugNotFoundError):
        shortener.lookup("does-not-exist")
