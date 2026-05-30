# spec: specs/url_utils.md::AC-2
"""leaf-02: behavioral tests for is_safe_url (spec lines 21-30)."""
from url_utils.is_safe_url import is_safe_url


def test_allowed_host_returns_true():
    # spec line 28
    assert is_safe_url("https://example.com/x", ["example.com"]) is True


def test_disallowed_host_returns_false():
    # spec line 29
    assert is_safe_url("https://evil.com/x", ["example.com"]) is False


def test_unparseable_url_returns_false_without_raising():
    # spec line 30
    assert is_safe_url("not-a-url", ["example.com"]) is False


def test_host_match_is_case_insensitive():
    # spec line 25 — "case-insensitive match on host"
    assert is_safe_url("https://EXAMPLE.com/x", ["example.com"]) is True
    assert is_safe_url("https://example.com/x", ["Example.COM"]) is True
