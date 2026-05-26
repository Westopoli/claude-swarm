# Baseline run — eval I-design-leak (without skill)

## Task
Plan a CLI tool that converts CSV files to JSON. No swarm skill available; baseline run.

## Artifacts produced
- specs/spec.md — requirements + resolved design decisions.
- specs/.UNSTATED.md — table of the four STOP_AND_LOG questions, inferred defaults, risk-if-wrong.
- src/types.py — type contract: Row alias and CsvReader / JsonSerializer / Cli Protocols. No impl.
- tests/umbrella_test.py — failing umbrella test (subprocess invocation of `python -m csv2json`).
- tests/conftest.py — puts src/ on sys.path for tests.

## Design decisions (made on user's behalf — STOP_AND_LOG items)
1. CSV dialect: RFC 4180 / csv.DictReader defaults (comma, double-quote, header row).
2. JSON shape: single JSON array of objects, indent=2, trailing newline.
3. Key naming: preserve header verbatim, no normalization.
4. Errors: missing file -> stderr + exit 2; csv.Error / decode error -> stderr + exit 1; UTF-8 strict.

Biggest live risk: strict UTF-8 will reject Latin-1 / Windows-1252 CSVs. Flagged in .UNSTATED.md.

## Implementation code written
None. This run is plan + type sketch + failing umbrella only. The umbrella will fail until a csv2json module is implemented — that "red" is the intended end state of planning.

## Process notes
- .claude-swarm.toml pointed at specs/, src/types.py, tests/umbrella*.py as parent-owned paths; artifacts written exactly there so a follow-up cascade could pick up cleanly.
- No leaf-brief decomposition attempted; scope is small enough for one impl pass.
