# spec: specs/url_utils.md::AC-1+AC-2::umbrella
"""Umbrella: end-to-end behaviour across both ACs. Starts RED."""
import pytest

from url_utils.types import ParsedUrl, parse_url, is_safe_url


def test_parse_then_safe_check_end_to_end():
    parsed = parse_url("https://Example.COM/path")
    assert parsed == ParsedUrl(scheme="https", host="example.com", path="/path")
    assert is_safe_url("https://example.com/path", ["example.com"]) is True
    assert is_safe_url("https://evil.com/path", ["example.com"]) is False
    assert is_safe_url("not-a-url", ["example.com"]) is False
