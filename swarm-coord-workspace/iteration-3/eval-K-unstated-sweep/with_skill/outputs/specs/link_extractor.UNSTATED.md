# Unstated assumptions for link_extractor

The user supplied a minimal description ("fetch a webpage and extract all
the links"). When the skill asked follow-up questions about specifics the
user had not addressed, the scripted response was `STOP_AND_LOG`, so each
unresolved detail is logged below with Disposition `flagged-for-spawn`
(per non-interactive fallback rule). The dispositions below also reflect
the user's blanket `accept-as-flagged` answer at the `.UNSTATED.md`
review gate.

## Entries

### U-1: Definition of "link"
- Artifact: spec, contract, umbrella
- Location: spec Acceptance criteria 3; `extract_links` return type; umbrella `EXPECTED_LINKS`
- Inferred value: links == values of `href` attributes on `<a>` elements in the parsed HTML. Other link-bearing constructs (`<link rel=...>`, `<area>`, `<iframe src>`, `<img src>`, JS-injected) are NOT included.
- Why this could not be cited: user said "all the links" but did not define which HTML elements/attributes count.
- Disposition: flagged-for-spawn

### U-2: Absolute vs relative URL handling
- Artifact: spec, contract
- Location: `extract_links` return type
- Inferred value: links are returned as written in the source HTML — no resolution against the base URL, no normalization.
- Why this could not be cited: user did not state whether relative hrefs should be resolved to absolute.
- Disposition: flagged-for-spawn

### U-3: Return container shape
- Artifact: contract
- Location: `extract_links` signature `-> list[str]`
- Inferred value: ordered `list[str]`, document order preserved, duplicates preserved.
- Why this could not be cited: user said "the links" — did not specify list vs set, ordering, or deduplication.
- Disposition: flagged-for-spawn

### U-4: HTTP client / fetch mechanism
- Artifact: contract
- Location: `extract_links` body (sentinel)
- Inferred value: not specified by the contract; leaf impl will choose (e.g., `urllib`, `requests`, `httpx`).
- Why this could not be cited: user said "fetch the page" but did not state a library or method.
- Disposition: flagged-for-spawn

### U-5: HTML parser choice
- Artifact: contract
- Location: `extract_links` body (sentinel)
- Inferred value: not specified by the contract; leaf impl will choose (e.g., `html.parser`, `beautifulsoup4`, `lxml`).
- Why this could not be cited: user said "parse it" but did not state a parser.
- Disposition: flagged-for-spawn

### U-6: Network-failure / HTTP-error semantics
- Artifact: spec, contract
- Location: `extract_links` behavior on non-200 / connection errors
- Inferred value: behavior unspecified — raise whatever the underlying fetch library raises.
- Why this could not be cited: user did not state what should happen on fetch failure.
- Disposition: flagged-for-spawn

### U-7: Timeout
- Artifact: spec, contract
- Location: `extract_links` signature (no timeout parameter)
- Inferred value: no explicit timeout. Whatever default the underlying client provides.
- Why this could not be cited: user did not state a timeout.
- Disposition: flagged-for-spawn

### U-8: Redirect handling
- Artifact: spec, contract
- Location: `extract_links` behavior
- Inferred value: follow redirects per the underlying client's default.
- Why this could not be cited: user did not state redirect policy.
- Disposition: flagged-for-spawn

### U-9: Encoding handling
- Artifact: spec, contract
- Location: `extract_links` behavior
- Inferred value: rely on the fetched response's declared content-type / charset; no explicit user-supplied encoding.
- Why this could not be cited: user did not state how non-UTF-8 pages should be decoded.
- Disposition: flagged-for-spawn

### U-10: Out-of-scope list
- Artifact: spec
- Location: "Out of scope" section
- Inferred value: empty / no items listed.
- Why this could not be cited: user answered "Not sure right now" for out-of-scope.
- Disposition: flagged-for-spawn

### U-11: Module path / function name
- Artifact: contract, umbrella
- Location: `src/types.py::extract_links`
- Inferred value: contract symbol named `extract_links`, located at `src/types.py` per `.claude-swarm.toml::type_contract_path`.
- Why this could not be cited: user did not state a function name.
- Disposition: flagged-for-spawn

### U-12: Umbrella fixture transport
- Artifact: umbrella
- Location: `tests/umbrella_test.py::_serve_fixture`
- Inferred value: serve the static HTML over loopback HTTP so the contract signature `extract_links(url: str)` can be exercised end-to-end. User said "small static HTML fixture" but did not say file-vs-server.
- Why this could not be cited: user described the fixture as "static HTML" but the contract takes a URL — bridging requires a transport choice.
- Disposition: flagged-for-spawn

### U-13: Project name / spec filename
- Artifact: spec, all artifact paths
- Location: `specs/link_extractor.md`
- Inferred value: `link_extractor` — derived mechanically from the user's intent ("fetches a webpage and extracts all the links").
- Why this could not be cited: user did not give the project a name.
- Disposition: flagged-for-spawn

### U-14: Any other detail not surfaced above
- Artifact: all
- Location: n/a
- Inferred value: any further design decision a leaf impl must make (logging, retries, user-agent header, robots.txt, SSL verification, etc.) is unresolved.
- Why this could not be cited: scripted follow-up response was `STOP_AND_LOG`; non-interactive fallback rule applies.
- Disposition: flagged-for-spawn
