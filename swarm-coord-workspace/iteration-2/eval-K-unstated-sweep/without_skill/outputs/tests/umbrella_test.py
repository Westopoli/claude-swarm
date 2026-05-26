"""Umbrella test: pins the 'done' definition for fetch_links.

Per the user: 'A test that calls the function on a small static HTML fixture
and gets back the expected list of links.'

This test is intentionally failing until fetch_links is implemented. It also
encodes (and therefore makes reviewable) the inferred decisions listed in
specs/spec.md:

  - anchors only (no <img>, <link>, <script>)
  - absolute URLs, resolved against the page URL
  - document order preserved
  - NOT deduplicated
  - empty / fragment-only / javascript: / mailto: hrefs dropped
  - non-2xx -> FetchError
  - non-HTML Content-Type -> ParseError
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.types import FetchError, ParseError, fetch_links


FIXTURE = Path(__file__).parent / "fixtures" / "sample.html"
PAGE_URL = "https://example.com/dir/page.html"


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200,
                 content_type: str = "text/html; charset=utf-8",
                 final_url: str = PAGE_URL):
        self.content = body
        self.text = body.decode("utf-8")
        self.status_code = status
        self.headers = {"Content-Type": content_type}
        self.url = final_url
        self.encoding = "utf-8"

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            import requests
            raise requests.HTTPError(f"{self.status_code}")


def _fake_get_html(*args, **kwargs):
    return _FakeResponse(FIXTURE.read_bytes())


def _fake_get_500(*args, **kwargs):
    return _FakeResponse(b"server error", status=500)


def _fake_get_pdf(*args, **kwargs):
    return _FakeResponse(b"%PDF-1.4 ...", content_type="application/pdf")


def test_extracts_expected_links_in_order_no_dedup():
    """Primary 'done' test the user described."""
    with patch("requests.get", side_effect=_fake_get_html):
        links = fetch_links(PAGE_URL)

    assert links == [
        "https://example.com/absolute",
        "https://example.com/relative/path",
        "https://example.com/dir/nested/page.html",
        "https://example.com/dup",
        "https://example.com/dup",  # NOT deduped
    ]


def test_non_2xx_raises_fetch_error():
    with patch("requests.get", side_effect=_fake_get_500):
        with pytest.raises(FetchError):
            fetch_links(PAGE_URL)


def test_non_html_raises_parse_error():
    with patch("requests.get", side_effect=_fake_get_pdf):
        with pytest.raises(ParseError):
            fetch_links(PAGE_URL)
