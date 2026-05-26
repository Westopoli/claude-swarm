"""Umbrella behavioral test for link_extractor.

Asserts user-visible behavior described in spec.md acceptance criterion 4:
"Calling the function on a small static HTML fixture returns the expected
list of links." [source: user-stmt-7]
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from src.types import extract_links


FIXTURE_HTML = b"""<!doctype html>
<html><body>
<a href="https://example.com/a">A</a>
<a href="https://example.com/b">B</a>
<a href="https://example.com/c">C</a>
</body></html>
"""


class _FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(FIXTURE_HTML)

    def log_message(self, *args, **kwargs):
        pass


def _serve_fixture():
    server = HTTPServer(("127.0.0.1", 0), _FixtureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_extract_links_returns_links_from_static_fixture():
    # spec.md acceptance criterion 4
    server = _serve_fixture()
    try:
        host, port = server.server_address
        url = f"http://{host}:{port}/"
        result = extract_links(url)
        # Behavioral assertion: return value contains the three fixture links.
        assert "https://example.com/a" in result
        assert "https://example.com/b" in result
        assert "https://example.com/c" in result
    finally:
        server.shutdown()
