# spec: specs/url_utils.md::AC-1::AC-1
"""Per-leaf RED test for AC-1 (parse_url). Owned by parent (overlord)."""
import pytest

from url_utils.types import ParsedUrl, parse_url


def test_parse_url_lowercases_scheme_and_host_preserves_path_case():
    result = parse_url("https://Example.COM/A/B")
    assert result == ParsedUrl(scheme="https", host="example.com", path="/A/B")


def test_parse_url_empty_path_becomes_slash():
    result = parse_url("http://example.com")
    assert result == ParsedUrl(scheme="http", host="example.com", path="/")


def test_parse_url_raises_when_scheme_missing():
    with pytest.raises(ValueError):
        parse_url("example.com/a")
