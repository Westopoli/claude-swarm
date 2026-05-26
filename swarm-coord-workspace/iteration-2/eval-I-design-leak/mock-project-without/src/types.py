"""Type contract for the csv2json CLI.

Minimal interfaces only — no implementation. Leaf agents fill these in.
"""

from __future__ import annotations

from typing import Protocol, Sequence


# A single parsed CSV row, header-keyed. All values are strings in v1.
Row = dict[str, str]


class CsvReader(Protocol):
    """Reads a CSV file from disk and yields header-keyed rows."""

    def read(self, path: str) -> list[Row]:
        """Return all rows as a list of dicts keyed by header.

        Raises:
            FileNotFoundError: if `path` does not exist.
            UnicodeDecodeError: if the file is not valid UTF-8.
            ValueError: wrapping csv.Error on malformed CSV.
        """
        ...


class JsonSerializer(Protocol):
    """Serializes a sequence of rows to a JSON string."""

    def dumps(self, rows: Sequence[Row]) -> str:
        """Return a JSON-array-of-objects string, pretty-printed."""
        ...


class Cli(Protocol):
    """Entry point. Returns a Unix exit code."""

    def main(self, argv: Sequence[str]) -> int:
        """Parse argv, run the conversion, write to stdout/stderr.

        Exit codes:
            0 — success
            1 — malformed CSV or decode error
            2 — missing / unreadable file or bad CLI usage
        """
        ...
