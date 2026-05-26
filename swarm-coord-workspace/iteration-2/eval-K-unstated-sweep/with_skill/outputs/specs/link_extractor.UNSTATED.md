# Unstated assumptions for link_extractor

## Entries

### U-1: Function name
- Artifact: contract
- Location: `src/types.py`, symbol `extract_links`
- Inferred value: `extract_links`
- Why this could not be cited: The user described the function ("a function that fetches a webpage and extracts all the links") but did not name it. Any concrete identifier here is the skill's pick.
- Disposition: flagged-for-spawn

### U-2: Output container type
- Artifact: contract, umbrella
- Location: `src/types.py` return annotation; umbrella `in` checks
- Inferred value: `list[str]` (an ordered list of string URLs)
- Why this could not be cited: User said "the links found on that page" — did not specify list vs set vs iterator vs generator, ordering guarantees, or de-duplication semantics.
- Disposition: flagged-for-spawn

### U-3: Link element scope (what counts as a "link")
- Artifact: spec, umbrella
- Location: spec acceptance criterion 3; umbrella fixture
- Inferred value: `<a href="...">` anchor elements only.
- Why this could not be cited: User said "all the links" without defining the term. Could plausibly include `<link>` tags, `<area>`, `<img src>`, `<script src>`, `<iframe src>`, form actions, CSS url(), etc.
- Disposition: flagged-for-spawn

### U-4: Absolute vs relative URL handling
- Artifact: contract, umbrella
- Location: umbrella fixture uses absolute URLs only; contract returns `list[str]` with no normalization promise
- Inferred value: Relative URLs are NOT resolved against the base URL — links are returned as written in the source HTML. (Side-stepped in the umbrella by using only absolute hrefs in the fixture.)
- Why this could not be cited: User did not state whether relative links should be resolved to absolute, left raw, or filtered out.
- Disposition: flagged-for-spawn

### U-5: HTTP request semantics (timeout, redirects, headers, user-agent)
- Artifact: contract
- Location: `extract_links(url: str)` signature has no timeout/redirect/header parameters
- Inferred value: Defaults left to the (downstream) HTTP library — no explicit timeout, redirects followed by default, no custom user-agent.
- Why this could not be cited: User said "fetch the page"; did not specify timeout, redirect policy, headers, or auth.
- Disposition: flagged-for-spawn

### U-6: Network / fetch failure semantics
- Artifact: contract
- Location: `extract_links` has no documented exception contract
- Inferred value: Errors propagate from the underlying HTTP/parse libraries (i.e., the function does not catch and translate them).
- Why this could not be cited: User did not state what should happen on DNS failure, timeout, non-2xx response, malformed HTML, or non-HTML content-type.
- Disposition: flagged-for-spawn

### U-7: HTTP / parser library choice
- Artifact: (implicit) downstream impl
- Location: not yet in any artifact; contract is library-agnostic
- Inferred value: Library choice deferred to leaf impl (e.g., `urllib`, `requests`, `httpx` for fetch; `html.parser`, `lxml`, `BeautifulSoup` for parse).
- Why this could not be cited: User stated "Python 3.11+" as the only constraint and did not pick libraries.
- Disposition: flagged-for-spawn

### U-8: Encoding / character-set handling
- Artifact: contract, umbrella
- Location: umbrella fixture serves `text/html; charset=utf-8`
- Inferred value: Pages are decoded according to the HTTP `Content-Type` charset or the document's declared encoding; pages without a declaration are assumed UTF-8.
- Why this could not be cited: User did not specify encoding behavior.
- Disposition: flagged-for-spawn

### U-9: Non-HTML / malformed content handling
- Artifact: contract
- Location: not specified anywhere
- Inferred value: Behavior on non-HTML responses (JSON, binary, empty body) or malformed HTML is undefined — propagates from parser.
- Why this could not be cited: User did not state.
- Disposition: flagged-for-spawn

### U-10: Spec name / artifact name
- Artifact: spec, contract, umbrella
- Location: filenames `link_extractor.md`, `extract_links` symbol
- Inferred value: `link_extractor` derived from the user's "extracts all the links" phrasing.
- Why this could not be cited: The user did not directly name the project/feature.
- Disposition: flagged-for-spawn

### U-11: Empty "Out of scope" section
- Artifact: spec
- Location: spec section "Out of scope"
- Inferred value: Treated user's "Not sure right now" as an empty out-of-scope list. This means nothing is explicitly excluded — downstream sweeps will need to revisit.
- Why this could not be cited: The user did not affirm or deny any specific item being out of scope.
- Disposition: flagged-for-spawn

### U-12: Umbrella fixture mechanism (local HTTP server vs file URL vs mocked HTTP client)
- Artifact: umbrella
- Location: `tests/umbrella_test.py` — uses an in-process `http.server.HTTPServer` on a random localhost port
- Inferred value: Use a real loopback HTTP server in-process to satisfy "fetches a webpage" without external network.
- Why this could not be cited: User said "small static HTML fixture" but did not say how it should be served (local file via `file://`, in-process HTTP, or HTTP mock library).
- Disposition: flagged-for-spawn

### U-13: De-duplication / ordering of returned links
- Artifact: contract, umbrella
- Location: `list[str]` return; umbrella uses `in` membership (does not assert order or uniqueness)
- Inferred value: No de-duplication; preserves document order. (Umbrella deliberately does not pin this — uses `in` not `==`.)
- Why this could not be cited: User did not state whether duplicates should be removed or in what order results should come.
- Disposition: flagged-for-spawn
