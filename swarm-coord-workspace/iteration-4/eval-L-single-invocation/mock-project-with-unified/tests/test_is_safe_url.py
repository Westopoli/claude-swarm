# spec: specs/url_utils.md::AC-2::AC-2
"""Per-leaf RED test for AC-2 (is_safe_url). Owned by parent (overlord)."""
from url_utils.types import is_safe_url


def test_is_safe_url_returns_true_when_host_allowed():
    assert is_safe_url("https://example.com/x", ["example.com"]) is True


def test_is_safe_url_returns_false_when_host_not_allowed():
    assert is_safe_url("https://evil.com/x", ["example.com"]) is False


def test_is_safe_url_returns_false_when_url_invalid_no_raise():
    assert is_safe_url("not-a-url", ["example.com"]) is False


def test_is_safe_url_case_insensitive_host_match():
    assert is_safe_url("https://EXAMPLE.com/x", ["Example.com"]) is True
