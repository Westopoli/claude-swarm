# claude-swarm config

Each project that uses the cascade skills places a `.claude-swarm.toml` at its git root. All three skills (`swarm`, `swarm-review`, `swarm-merge`) read it. Missing file is fine — defaults apply.

## Schema

```toml
# Paths — all relative to git root unless noted

spec_dir          = "specs/"
briefs_dir        = ".swarm/briefs/"
questions_dir     = ".swarm/questions/"   # leaves publish here, parent reads
answers_dir       = ".swarm/answers/"     # parent publishes here, leaves consume
proposals_dir     = ".swarm/proposals/"   # leaves propose parent-owned-file changes
type_contract_path = "src/<pkg>/types.py"

# Test + dependency-map commands. The skill shells out exactly as written.

umbrella_test_cmd = "pytest tests/umbrella.py"
# Optional: behavioral integration test run by /swarm-merge at queue completion.
# Distinct from umbrella_test_cmd (which is per-leaf-isolation). Catches the
# failure mode where every leaf's umbrella was a source-grep pattern but the
# integrated behavior is still broken.
apex_test_cmd     = ""
graphify_cmd      = ""                   # empty string → fall back to import-graph heuristic

# Optional: paths excluded from G5 wave-snapshot integrity check.
# Defaults below. Add project-specific generated dirs as needed.
snapshot_ignore   = [
  ".git/**", ".swarm/**", "__pycache__/**",
  "node_modules/**", ".venv/**", "*.pyc",
]

# Files the parent owns. Globs. No leaf may name a file matching these.

parent_owned = [
  "src/**/types.py",
  "tests/conftest.py",
  "tests/umbrella*.py",
  "tests/integration/**",
]

[invariants]
max_impl_lines        = 200
max_test_assertions   = 20

# Words that, if found in a brief's task prose, indicate a design decision
# is being delegated to the leaf. /swarm-review fails the brief.
ambiguous_verbs = [
  "decide", "choose", "design", "determine",
  "figure out", "resolve", "as appropriate",
  "use your judgment", "pick", "select an approach",
]

[gates]
# Optional project-specific gates run before /swarm continues past spec-gate.
# Each entry is a shell command. Non-zero exit blocks. Empty list = no extra gates.
# $SPEC_FILE is exported by the skill before each command.
extra_spec_gate_cmds = []

# Example: require spec to contain a compliance-report section.
# extra_spec_gate_cmds = [
#   "grep -q '^## Compliance Report' \"$SPEC_FILE\"",
# ]
```

## Defaults

If `.claude-swarm.toml` is missing, the skill uses every default above. `type_contract_path` has no sensible global default — the skill asks the user once and writes a `.claude-swarm.toml` with the answer.

## Precedence

1. `.claude-swarm.toml` at git root.
2. Built-in defaults.

Environment variables can override individual keys for one-off runs: `CLAUDE_SWARM_SPEC_DIR=alt-specs/ /swarm`.

## Why a config file rather than CLI flags

The cascade is a workflow, not a one-shot script. A given project always slices the same way; encoding the parameters once means the slash command stays short and the audit results stay reproducible across sessions.
