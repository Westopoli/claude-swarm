# CSV-to-JSON CLI — Spec

## Goal
A small command-line tool that reads a CSV file from disk and writes its
contents to stdout as JSON.

## Inputs
- **arg 1 (positional, required):** path to a CSV file on disk.

## Outputs
- JSON written to **stdout**.
- Diagnostics (errors, warnings) written to **stderr**.

## Behavior
1. Open the file at the given path.
2. Parse it as CSV (header row + data rows).
3. Convert each data row into a JSON object keyed by the header names.
4. Serialize the list of objects to stdout as JSON.

## Constraints
- Python **3.11+**.
- **Standard library only** — no pandas, no external dependencies.

## Out of Scope
- Writing output to a file (callers use shell redirection: `tool x.csv > x.json`).
- Multi-file conversion / globbing.
- Streaming for files that don't fit in memory.
- Schema inference / type coercion (everything is a string in v1).

## "Done" — Umbrella Acceptance
Run the CLI against a small CSV fixture, capture stdout, assert it parses as
JSON and contains the expected rows.

## Resolved Design Decisions (flagged — see .UNSTATED.md)
The user declined to specify these four; the defaults below are chosen by
the planner and should be confirmed before lock-in.

1. **CSV dialect** — RFC 4180 defaults: comma delimiter, double-quote quoting,
   first row is the header. Implemented via `csv.DictReader` defaults.
2. **JSON output shape** — single JSON **array of objects**, pretty-printed
   with 2-space indentation, trailing newline.
3. **Key naming** — header names preserved verbatim (no case folding,
   no whitespace trimming beyond what `csv` already does).
4. **Error behavior**
   - Missing / unreadable file -> stderr message, exit code **2**.
   - Malformed CSV (e.g. `csv.Error`) -> stderr message, exit code **1**.
   - Encoding: UTF-8, strict. Decode errors -> stderr + exit code **1**.
   - Success -> exit code **0**.

## CLI Surface
```
csv2json PATH
```
No flags in v1. `--help` / `-h` produces standard argparse usage text.
