"""Type contract for csv-to-json.

Symbols here are imported by the umbrella test. Bodies are sentinels; real
behavior is filled in by downstream leaf agents (see /swarm-spawn).
"""

from __future__ import annotations


def convert_csv_to_json(csv_path: str) -> str:
    """Convert the CSV file at ``csv_path`` to a JSON string.

    Encodes spec acceptance criteria 2 and 3 (read CSV at path, produce JSON
    output). The CLI entry point writes the returned string to stdout, which
    satisfies acceptance criterion 3.

    # encodes specs/csv-to-json.md acceptance criteria 1-4 (input path,
    # row-to-object conversion, JSON output, fixture-driven umbrella).
    """
    raise NotImplementedError
