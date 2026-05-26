"""Umbrella test — pins the 'done' definition for the csv2json CLI.

Runs the CLI as a subprocess against a tiny fixture, captures stdout,
asserts it parses as JSON and contains the expected rows.

This test should FAIL until the implementation lands. That failure is the
contract every leaf agent is working against.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


FIXTURE_CSV = """name,age,city
Ada,36,London
Grace,85,New York
Linus,55,Helsinki
"""

EXPECTED_ROWS = [
    {"name": "Ada", "age": "36", "city": "London"},
    {"name": "Grace", "age": "85", "city": "New York"},
    {"name": "Linus", "age": "55", "city": "Helsinki"},
]


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "people.csv"
    p.write_text(FIXTURE_CSV, encoding="utf-8")
    return p


def _run_cli(csv_path: Path) -> subprocess.CompletedProcess[str]:
    # Invoke as a module so we don't depend on console_scripts install.
    return subprocess.run(
        [sys.executable, "-m", "csv2json", str(csv_path)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_converts_csv_to_json_on_stdout(csv_file: Path) -> None:
    result = _run_cli(csv_file)

    assert result.returncode == 0, f"stderr was: {result.stderr!r}"
    assert result.stdout, "expected JSON on stdout, got empty string"

    parsed = json.loads(result.stdout)
    assert parsed == EXPECTED_ROWS
