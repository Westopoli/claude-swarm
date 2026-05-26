"""Umbrella test for url_shortener.

Behavioral assertions only. Imports from the type contract (src.types) and
asserts on return values / observable side effects. Expected RED until leaves
implement the contract.
"""

from src.types import shorten, lookup, redirect


def test_round_trip_and_redirect():
    # acceptance criterion 1: shorten returns a slug string
    long_url = "https://example.com/some/very/long/path?q=1"
    slug = shorten(long_url)
    assert isinstance(slug, str)
    assert slug  # non-empty

    # acceptance criterion 2: lookup on that slug returns the original URL
    assert lookup(slug) == long_url

    # acceptance criterion 3: visiting the slug returns 302 with Location == original URL
    status, headers = redirect(slug)
    assert status == 302
    header_map = {name.lower(): value for name, value in headers}
    assert header_map.get("location") == long_url
