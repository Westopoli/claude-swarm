# Unstated assumptions for csv-to-json

## Entries

### U-1: CSV dialect (delimiter, quoting, header row)
- Artifact: spec, umbrella
- Location: spec acceptance criterion 2; umbrella fixture in tests/umbrella_test.py (`_write_fixture`).
- Inferred value: Standard `,`-delimited CSV with a single header row on line 1. Quoting follows Python's `csv` module default dialect (RFC 4180-ish). Fixture uses `name,age\nalice,30\nbob,25\n`.
- Why this could not be cited: The user did not state a CSV dialect when asked. Response was STOP_AND_LOG.
- Disposition: flagged-for-spawn

### U-2: JSON output shape (array of objects vs newline-delimited)
- Artifact: contract, umbrella
- Location: `convert_csv_to_json` return type in `src/types.py`; umbrella assertion in `test_convert_csv_to_json_contains_expected_rows`.
- Inferred value: A single JSON string returned from `convert_csv_to_json`. Whether that string is an array-of-objects (`[{"name":"alice",...}, ...]`) or newline-delimited JSON (one object per line) is left unresolved. The umbrella asserts on serialized-substring presence so either shape can satisfy it.
- Why this could not be cited: The user did not state a JSON output shape when asked. Response was STOP_AND_LOG.
- Disposition: flagged-for-spawn

### U-3: Key naming convention (preserve casing vs snake_case)
- Artifact: contract, umbrella
- Location: implicit in `convert_csv_to_json`'s output keys; umbrella assertion uses literal `"alice"`/`"bob"` values rather than key names.
- Inferred value: Keys in the JSON output use the CSV header strings verbatim, no casing transformation. The umbrella deliberately asserts on values only, so the test does not pin a key-casing choice.
- Why this could not be cited: The user did not state a key-naming convention when asked. Response was STOP_AND_LOG.
- Disposition: flagged-for-spawn

### U-4: Error behavior (missing file, malformed row, encoding)
- Artifact: contract
- Location: `convert_csv_to_json` signature in `src/types.py` (no documented exception contract).
- Inferred value: No specific error contract. On missing file the implementation will surface whatever exception the standard-library `open(...)` raises (`FileNotFoundError`). On malformed rows or non-UTF-8 encoding the behavior is undefined and will surface whatever the `csv` and `json` modules raise. The umbrella does not exercise error paths.
- Why this could not be cited: The user did not state error semantics when asked. Response was STOP_AND_LOG.
- Disposition: flagged-for-spawn

### U-5: Contract return type (`str` vs direct stdout write)
- Artifact: contract
- Location: `convert_csv_to_json` signature in `src/types.py`.
- Inferred value: The contract function returns a `str` (the JSON text) rather than writing directly to stdout. The CLI entry point — which is not part of this contract — is the layer that writes to stdout. This choice makes the umbrella testable without subprocess capture.
- Why this could not be cited: The user said "JSON written to stdout" (user-stmt-3) but did not specify whether the conversion primitive returns a string or writes directly. The split between a string-returning conversion function and a stdout-writing CLI entry point is the skill's inference.
- Disposition: flagged-for-spawn

### U-6: CLI entry point shape
- Artifact: spec
- Location: spec acceptance criterion 1 says "accepts a CSV file path as its first positional CLI argument" but the contract does not yet declare a CLI entry function.
- Inferred value: The contract exposes only `convert_csv_to_json(csv_path: str) -> str`. A separate CLI entry point (parsing `sys.argv[1]`, calling the conversion, and printing the result) is left for a downstream leaf brief. The umbrella does not exercise the CLI directly; it calls the conversion primitive.
- Why this could not be cited: The user described CLI behavior (user-stmt-1, user-stmt-2) but did not specify where in the type contract the CLI entry point lives, or whether it is a callable, a `__main__` block, or a console script.
- Disposition: flagged-for-spawn
