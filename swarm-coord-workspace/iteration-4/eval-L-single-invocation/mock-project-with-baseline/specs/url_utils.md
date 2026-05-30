# url_utils — spec

A tiny URL utility module with two independent capabilities.

## Source of truth

This mock project has no upstream bible doc. Spec stands alone.

## AC-1 — `parse_url(url: str) -> ParsedUrl`

Given a URL string, return a `ParsedUrl` dataclass with fields:
- `scheme: str` — lowercased scheme (e.g. `"https"`)
- `host: str` — lowercased host (e.g. `"example.com"`)
- `path: str` — path component, including leading slash (e.g. `"/a/b"`); `"/"` if URL has no path

Behaviour:
- `parse_url("https://Example.COM/A/B")` → `ParsedUrl(scheme="https", host="example.com", path="/A/B")`. Path case is preserved; scheme/host are lowercased.
- `parse_url("http://example.com")` → `ParsedUrl(scheme="http", host="example.com", path="/")`.
- Raises `ValueError` for inputs missing a scheme (e.g. `"example.com/a"`).

## AC-2 — `is_safe_url(url: str, allowed_hosts: list[str]) -> bool`

Given a URL string and a list of allowed hosts, return `True` iff:
- `parse_url(url)` succeeds (does not raise), AND
- the parsed `host` is in `allowed_hosts` (case-insensitive match on host).

Examples:
- `is_safe_url("https://example.com/x", ["example.com"])` → `True`
- `is_safe_url("https://evil.com/x", ["example.com"])` → `False`
- `is_safe_url("not-a-url", ["example.com"])` → `False` (does NOT raise)

## Decomposition guidance

- Leaf-1: implement `parse_url` + `ParsedUrl`. Test file: `tests/test_parse_url.py`.
- Leaf-2: implement `is_safe_url`. Test file: `tests/test_is_safe_url.py`. Imports `parse_url` from leaf-1 (read-only dependency).

## Bible Compliance

- **Bible path:** none — this project has no source-of-truth doc.
- **Sections referenced:** N/A.
- **Deliberate divergences:** none.
