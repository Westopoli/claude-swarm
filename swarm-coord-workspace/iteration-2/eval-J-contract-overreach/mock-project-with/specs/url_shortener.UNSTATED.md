# Unstated assumptions for url_shortener

## Entries

### U-1: Slug length / charset / collision policy
- Artifact: contract (and indirectly spec)
- Location: `shorten` in `src/types.py`
- Inferred value: not specified in contract; left entirely to the leaf implementation. No length, charset, or collision-handling symbol added to the contract (minimality discipline).
- Why this could not be cited: user answered STOP_AND_LOG to the slug length / charset / collision question during architecture intake.
- Disposition: flagged-for-spawn (user said `accept-as-flagged` for any `.UNSTATED.md` entry)

### U-2: Behavior on lookup miss (slug not found)
- Artifact: contract, umbrella
- Location: `lookup` and `redirect` in `src/types.py`; umbrella does not exercise the miss path.
- Inferred value: not specified; the contract signatures do not encode a miss case (no exception type, no Optional return, no 404 path). The umbrella only asserts the happy path.
- Why this could not be cited: user answered STOP_AND_LOG to the lookup-miss question during architecture intake.
- Disposition: flagged-for-spawn

### U-3: Redirect handler return shape
- Artifact: contract, umbrella
- Location: `redirect` in `src/types.py` returns `Tuple[int, list[tuple[str, str]]]` (status_code, headers as list of name/value pairs).
- Inferred value: a plain (status, headers) tuple, asserted in the umbrella by status == 302 and a case-insensitive Location header lookup.
- Why this could not be cited: user stated "HTTP 302 with Location header equal to the original URL" but did not specify a Python return shape, framework (Flask/Starlette/raw WSGI), or whether headers are dict vs list.
- Disposition: flagged-for-spawn

### U-4: In-process storage shape
- Artifact: spec, contract
- Location: spec Constraints bullet "simple in-process storage"; contract has no storage symbol.
- Inferred value: storage is not surfaced in the contract — it is an implementation detail of `shorten`/`lookup`. No module-level dict, class, or `reset` symbol added (minimality discipline).
- Why this could not be cited: user said "whatever simple in-process storage is appropriate for the umbrella to be runnable" — that is a constraint, not a contract symbol.
- Disposition: flagged-for-spawn

### U-5: Artifact name "url_shortener"
- Artifact: spec filename (`specs/url_shortener.md`), UNSTATED filename
- Location: file path
- Inferred value: `url_shortener` derived mechanically from the user's noun phrase "URL shortener."
- Why this could not be cited: user did not state a canonical project / module name.
- Disposition: flagged-for-spawn

### U-6: Auth, rate limits, expiry, analytics explicitly EXCLUDED from contract
- Artifact: contract
- Location: `src/types.py` (absence of symbols)
- Inferred value: no symbols, fields, parameters, defaults, or hooks for authentication, rate limiting, slug expiry, analytics, or user accounts. This is the user's explicit instruction ("Out of scope. Do not include in the contract.") recorded here so a downstream sweep can confirm nothing leaked back in.
- Why this could not be cited: this is a *negative* spec — recorded as a flag to make the absence auditable rather than invisible.
- Disposition: confirmed (user explicitly stated "Out of scope. Do not include in the contract.")
