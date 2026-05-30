# spec: specs/url_utils.md::AC-1
"""leaf-01: behavioral tests for parse_url (spec lines 9-19)."""
import pytest

from url_utils.types import ParsedUrl
from url_utils.parse_url import parse_url


def test_lowercases_scheme_and_host_preserves_path_case():
    # spec line 17
    assert parse_url("https://Example.COM/A/B") == ParsedUrl(
        scheme="https", host="example.com", path="/A/B"
    )


def test_empty_path_normalizes_to_slash():
    # spec line 18
    assert parse_url("http://example.com") == ParsedUrl(
        scheme="http", host="example.com", path="/"
    )


def test_missing_scheme_raises_value_error():
    # spec line 19
    with pytest.raises(ValueError):
        parse_url("example.com/a")
