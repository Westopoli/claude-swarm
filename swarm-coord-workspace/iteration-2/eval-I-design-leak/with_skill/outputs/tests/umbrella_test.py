"""Umbrella test for csv-to-json.

Behavioral assertions only — no source-grep. Imports from the type contract
(src/types.py) and asserts on the return value of ``convert_csv_to_json``.

Encodes spec acceptance criterion 4: "Running the CLI against a small CSV
fixture and capturing stdout yields output that parses as JSON and contains
the expected rows."
"""

from __future__ import annotations

import json
from pathlib import Path

from src.types import convert_csv_to_json


def _write_fixture(tmp_path: Path) -> Path:
    """Write a small CSV fixture and return its path.

    The exact CSV dialect (delimiter, quoting, header row) is an UNSTATED
    inference flagged in specs/csv-to-json.UNSTATED.md (U-1).
    """
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("name,age\nalice,30\nbob,25\n", encoding="utf-8")
    return csv_path


def test_convert_csv_to_json_returns_parseable_json(tmp_path: Path) -> None:
    """Acceptance criterion 4: output parses as JSON."""
    csv_path = _write_fixture(tmp_path)

    result = convert_csv_to_json(str(csv_path))

    # Behavioral: the return value must be JSON-parseable text.
    parsed = json.loads(result)
    assert parsed is not None


def test_convert_csv_to_json_contains_expected_rows(tmp_path: Path) -> None:
    """Acceptance criterion 4: parsed output contains the expected rows.

    The exact JSON shape (array of objects vs newline-delimited) and key
    casing are UNSTATED inferences flagged in specs/csv-to-json.UNSTATED.md
    (U-2, U-3). This assertion looks for the row *values* anywhere in the
    parsed structure so it survives either shape until the user resolves
    those flags.
    """
    csv_path = _write_fixture(tmp_path)

    result = convert_csv_to_json(str(csv_path))
    parsed = json.loads(result)

    serialized = json.dumps(parsed)
    assert "alice" in serialized
    assert "bob" in serialized
    assert "30" in serialized or 30 in json.loads(serialized) or "30" in serialized
