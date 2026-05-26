# Spec: fetch_links

## One-line summary
A function that fetches a webpage over HTTP(S) and returns the list of links
found on that page.

## User-stated requirements (verbatim)
- Input: a URL string.
- Output: the links found on that page.
- Behavior: fetch the page, parse it, return the links.
- Constraint: Python 3.11+.
- "Done" = a test that calls the function on a small static HTML fixture and
  gets back the expected list of links.

## Out of scope (user-stated)
- Not specified by user.

---

## Inferred decisions (UNSTATED — user answered STOP_AND_LOG)

The user did not answer the follow-up question covering timeout, link
definition, redirect handling, encoding, network failure, output format, and
absolute-vs-relative URLs. Per the eval playbook's non-interactive mode, the
following defaults are recorded here so they are visible, not silently buried
in code. Each is a candidate for revision once the user is available.

| # | Topic | Decision | Rationale |
|---|---|---|---|
| 1 | What counts as a "link" | `<a href="...">` only (not `<img src>`, `<link href>`, `<script src>`, `<form action>`, etc.) | Common-sense default; "links" in user vernacular almost always means anchor hrefs. Other resource URLs are a separate feature. |
| 2 | Absolute vs relative URLs | Return URLs **resolved against the page's base URL** (so the caller gets absolute URLs they can re-fetch). Empty / `javascript:` / `mailto:` / `#fragment-only` hrefs are dropped. | Useful default; raw hrefs are usually not what callers want. |
| 3 | Deduplication / order | Preserve document order; do NOT deduplicate. | Order is information; dedup is trivial for the caller if they want it. |
| 4 | HTTP timeout | 10 seconds (connect+read combined). | Sensible default; long enough for slow pages, short enough not to hang tests. |
| 5 | Redirect handling | Follow up to 5 redirects. Link resolution uses the **final** URL as the base. | Matches `requests` library default; what most users mean. |
| 6 | Encoding | Honor `Content-Type` charset; fall back to UTF-8; if the body declares a `<meta charset>`, prefer that. | Standard HTML parsing behavior. |
| 7 | Network / HTTP failure | Raise an exception (do not return an empty list). Distinct exception types for: network/timeout error, non-2xx HTTP status, parse error. | "Empty list" silently hides bugs. Exceptions force the caller to decide. |
| 8 | Non-HTML responses | If `Content-Type` is not `text/html` (or `application/xhtml+xml`), raise a parse-type error rather than attempting to extract links from binary/JSON. | Avoids garbage-in-garbage-out. |
| 9 | Output format | `list[str]` of absolute URL strings. | Simplest type that matches the user's stated output. |
| 10 | HTTP library | `requests` (sync). | Sync is enough; matches the "function" framing. |
| 11 | HTML parser | `beautifulsoup4` with the stdlib `html.parser` backend (no extra C deps). | Tolerant of real-world malformed HTML. |
| 12 | User-Agent header | A fixed, identifying UA string (e.g. `fetch-links/0.1`). | Some servers reject empty/default UAs. |

---

## API contract (informal)

```python
def fetch_links(url: str, *, timeout: float = 10.0) -> list[str]: ...
```

- `url`: absolute http(s) URL.
- `timeout`: per-request seconds.
- Returns: list of absolute URL strings, in document order, no dedup.
- Raises:
  - `FetchError` — network failure, timeout, or non-2xx status.
  - `ParseError` — response is not HTML / cannot be parsed.

See `src/types.py` for the formal contract.

## Definition of done
- `tests/umbrella_test.py` passes: a static HTML fixture is fed to
  `fetch_links` (network mocked) and the returned list matches the expected
  set of resolved absolute URLs in document order.
