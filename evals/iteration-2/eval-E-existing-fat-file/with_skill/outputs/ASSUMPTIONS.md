## Assumptions made during /tdd-root

- **spec_file**: `inputs/specs/wave-3.md` — source: explicit in eval invocation prompt
- **wave**: 3 — source: spec filename (`wave-3.md`) and spec title "Wave-3 Spec"
- **expected_leaf_count**: 3 — source: spec has exactly three ACs (AC1 upsert, AC2 tag, AC3 custom field), each maps to one leaf
- **strategy_doc_path**: none provided — source: no bible path given in invocation or config; eval scenario omits it; assumed N/A for this batch
- **strategy_changes_since_last**: unknown — no source available; eval scenario does not provide this
- **out_of_scope**: `validate_ops()`, `order_ops()`, `batch_emit()` integration — source: spec lines 27-31 ("Out of scope" section)
- **brief_reviewer**: assumed /tdd-review only — source: default per skill intake Q7; eval scenario does not specify
- **existing_files**: yes — source: explicit in eval invocation prompt ("modifying existing"); `src/myproj/sync_ops.py` already exists in inputs/
