# URL Shortener — Spec

## Goal
A simple URL shortener. The user submits a long URL and gets back a short slug. Visiting the short slug redirects to the long URL.

## Inputs
- A long URL string from the user.

## Outputs
- A short slug string (from `shorten`).
- An HTTP 302 redirect with `Location` header equal to the original URL (from the redirect handler).

## Main Behaviors
1. `shorten(long_url: str) -> str` — returns a slug for the given URL.
2. `lookup(slug: str) -> str` — returns the long URL previously associated with the slug.
3. HTTP redirect handler — given a slug, return HTTP 302 with `Location: <long_url>`. Uses `lookup` internally.

## Constraints
- Python 3.11+.
- In-process storage only (e.g., a dict). No persistence across process restart.
- Library/handler form must be runnable in pytest.

## Out of Scope (explicit)
- Persistence across process restart.
- User accounts / authentication.
- Analytics.
- Rate limiting.
- Slug expiry.
- Custom slugs.

## Definition of Done (umbrella)
- `shorten(long_url)` returns a non-empty slug.
- `lookup(slug)` on that slug returns the original `long_url`.
- Visiting the slug via the HTTP handler returns status `302` with `Location` equal to `long_url`.

## Unstated / Inferred (flagged)
These were `STOP_AND_LOG` in intake and resolved with best-judgment defaults:

- **Slug length / charset / collision policy**: default to 7-character slugs from the URL-safe alphabet `[A-Za-z0-9]` (62^7 ≈ 3.5 trillion). On collision, regenerate up to 5 times; if still colliding, raise `CollisionError`. Disposition: accept-as-flagged.
- **Lookup miss behavior**: `lookup(slug)` raises `SlugNotFoundError` when the slug is unknown. The HTTP handler maps this to HTTP `404`. Disposition: accept-as-flagged.
- **Idempotency on repeat `shorten` of same URL**: not specified. Default: each call returns a fresh slug (no dedup). Disposition: accept-as-flagged.
- **URL validation**: not specified. Default: accept any non-empty string; do not validate scheme. Disposition: accept-as-flagged.
