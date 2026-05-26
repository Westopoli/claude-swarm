"""Umbrella test for link_extractor.

Behavioral assertion only. Imports from the type contract (src/types.py)
and asserts on the function's return value when called on a static HTML
fixture. Expected to be RED until the leaf impl lands.

Encodes acceptance criterion 4 (spec.md):
"A test calling the function on a small static HTML fixture returns the
expected list of links." [source: user-stmt-9]
"""

from __future__ import annotations

import http.server
import threading
from contextlib import contextmanager

from src.types import extract_links


FIXTURE_HTML = b"""<!doctype html>
<html><body>
  <a href="https://example.com/one">one</a>
  <a href="https://example.com/two">two</a>
  <a href="https://example.com/three">three</a>
</body></html>
"""

EXPECTED_LINKS = [
    "https://example.com/one",
    "https://example.com/two",
    "https://example.com/three",
]


class _FixtureHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(FIXTURE_HTML)))
        self.end_headers()
        self.wfile.write(FIXTURE_HTML)

    def log_message(self, format, *args):  # silence test output
        return


@contextmanager
def _serve_fixture():
    server = http.server.HTTPServer(("127.0.0.1", 0), _FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/"
    finally:
        server.shutdown()
        server.server_close()


def test_extract_links_returns_expected_links_from_static_fixture():
    # Behavioral: call the contract symbol on a static HTML fixture served
    # over loopback, assert the returned links match the expected set.
    with _serve_fixture() as url:
        result = extract_links(url)
    assert list(result) == EXPECTED_LINKS
