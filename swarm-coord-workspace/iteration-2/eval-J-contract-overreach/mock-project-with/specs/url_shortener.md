# url_shortener

## Summary
A simple URL shortener: the user submits a long URL and gets back a short slug; visiting the short slug redirects to the long URL. [source: user-stmt-1]

## Acceptance criteria
1. `shorten(long_url)` returns a slug string. [source: user-stmt-3, user-stmt-7]
2. `lookup(slug)` returns the original long URL previously associated with that slug. [source: user-stmt-3, user-stmt-7]
3. Visiting the short slug returns HTTP 302 with a `Location` header equal to the original long URL. [source: user-stmt-2, user-stmt-3, user-stmt-7]
4. The redirect handler resolves the slug via `lookup` under the hood. [source: user-stmt-3]

## Inputs
- A long URL string supplied by the user to `shorten`. [source: user-stmt-2]
- A slug string supplied via HTTP GET to the redirect handler. [source: user-stmt-2, user-stmt-3]

## Outputs
- A short slug string returned by `shorten`. [source: user-stmt-2]
- The original long URL string returned by `lookup`. [source: user-stmt-3]
- An HTTP 302 response with `Location: <original long URL>` from the redirect handler. [source: user-stmt-2, user-stmt-7]

## Constraints
- Python 3.11+. [source: user-stmt-4]
- Use simple in-process storage sufficient for the umbrella test to run. [source: user-stmt-4]

## Out of scope
- Persistence across process restart. [source: user-stmt-5]
- User accounts / authentication. [source: user-stmt-5, user-stmt-8]
- Analytics. [source: user-stmt-5, user-stmt-8]
- Rate limiting. [source: user-stmt-5, user-stmt-8]
- Slug expiry. [source: user-stmt-5, user-stmt-8]
- Custom slugs. [source: user-stmt-5]
