# csv-to-json

## Summary
A CLI tool that converts a CSV file on disk into JSON written to standard output. The user passes a CSV file path as the first positional argument and reads the resulting JSON from stdout. [source: user-stmt-1]

## Acceptance criteria
1. The tool accepts a CSV file path as its first positional CLI argument. [source: user-stmt-2]
2. The tool reads the CSV at that path and converts each row to a JSON object. [source: user-stmt-4]
3. The tool writes the resulting JSON to stdout. [source: user-stmt-3]
4. Running the CLI against a small CSV fixture and capturing stdout yields output that parses as JSON and contains the expected rows. [source: user-stmt-7]

## Inputs
- A filesystem path to a CSV file, passed as the first positional CLI argument. [source: user-stmt-2]

## Outputs
- JSON written to stdout. [source: user-stmt-3]

## Constraints
- Implementation language is Python 3.11+. [source: user-stmt-5]
- Standard library only — no pandas, no external dependencies. [source: user-stmt-5]

## Out of scope
- Writing the JSON to a file directly (the user redirects stdout instead). [source: user-stmt-6]
- Multi-file conversion in a single invocation. [source: user-stmt-6]
