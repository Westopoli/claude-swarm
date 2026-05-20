# Assumption-sweep report — iteration-2

## Summary
- Total assumptions logged: 18
- Flagged: 4
- Unflagged: 14

Counts per eval:
- eval-A: 4 assumptions logged → 2 flagged
- eval-B: 9 assumptions logged → 1 flagged
- eval-C: 7 assumptions logged → 1 flagged (moot — skill halted correctly)
- eval-D: 5 assumptions logged → 0 flagged (1 notable edge observed)

---

## Flagged entries

### [eval-A / Assumption 1 — leaf-09 CachePolicy contract import]

- **Assumption:** Not explicitly logged in REVIEW_ASSUMPTIONS.md; the brief itself was passed through as-is. The audit tool consumed it and reported `Type contract symbols` from types.py as: AggregatedRow, WindowSpec, RollupKey, DashboardView, FilterPredicate, MetricDef, TimeRange, BucketSize, ResultRow, ErrorReport.
- **Finding:** `leaf-09` declares `contract_imports: [CachePolicy, ResultRow]`. `CachePolicy` does not exist in `src/myproj/types.py`. It is not in the 10-symbol contract.
- **Classification:** `fabricated` — references a type that does not exist in the shared contract.
- **Conflicts with:** `src/myproj/types.py` (eval-A ground truth). `CachePolicy` has no definition in the file. The `.tdd-cascade.toml` `type_contract_path` points to that file and it is the only allowlist source.
- **Damage assessment:** Leaf-09 will fail import at test time. Any test that constructs or type-checks `CachePolicy` cannot pass. The leaf agent will import a non-existent symbol and either get `ImportError` immediately or fabricate its own definition — both outcomes violate the shared-type contract rule ("No leaf edits it").
- **Patch suggestion (no redo):** Parent must add `CachePolicy` to `src/myproj/types.py` before leaf-09 is spawned, or revise leaf-09's brief to use an existing type (e.g., `ResultRow` only, with cache-key logic encoded differently). Do not let leaf-09 run with the current contract_imports field.

---

### [eval-A / Assumption 2 — leaf-07 and leaf-12 share impl_file]

- **Assumption (from REVIEW_ASSUMPTIONS.md, Inferred Answer #2):** "Both leaf-07 and leaf-12 are in wave 2 and claim the same impl_file, so this is unambiguously a same-wave overlap."
- **Finding:** Confirmed by ground truth. leaf-07 `impl_file: src/myproj/aggregator/window.py` (wave 2) and leaf-12 `impl_file: src/myproj/aggregator/window.py` (wave 2). This is a hard invariant violation: two wave-2 leaves own the same implementation file.
- **Classification:** `cross-leaf` — two agents made incompatible assignments about the same shared file. (The REVIEW_ASSUMPTIONS.md correctly detected this; the flag is against the underlying brief set, not the assumption log.)
- **Conflicts with:** tdd-cascade non-overlap invariant. Two leaves in the same wave cannot share an impl_file. leaf-07 task is "sliding-window" and leaf-12 task is "tumbling-window" — these are distinct behaviors that the parent decomposed incorrectly into a single file.
- **Damage assessment:** If both leaf agents run concurrently, they will overwrite each other's work. Whichever commits last wins; the other's tests will either pass accidentally or fail because their expected behavior is gone. The umbrella will see non-deterministic results depending on merge order.
- **Patch suggestion (no redo):** Split `window.py` into `window_slide.py` (leaf-07) and `window_tumble.py` (leaf-12). Update each brief's `impl_file`, `test_file`, and any cross-references. The do_not_edit lists for each leaf must list the other's new file. Do not spawn either leaf until the split is done.

---

### [eval-B / Assumption — bucket_id label format cross-leaf dependency]

- **Assumption (ASSUMPTIONS.md):** "bucket_id representation: string label for each bucket, e.g. `bucket_0`, `bucket_1` — source: AggregatedRow.bucket_id is typed str in types.py; spec does not prescribe format; labeled as assumption in leaf-01 brief"
- **Finding:** The spec (`feature-aggregator.md`) does not prescribe the `bucket_id` format. The assumption acknowledges this. However, leaf-02 (sliding.py) is directed to use "whatever `buckets.py` returns" (from the emitted leaf-02 brief). Leaf-02's escalation trigger explicitly says: "The bucket_id label format produced by buckets.py differs from what your test expects — escalate, do not adapt silently." The assumption in leaf-01 (which controls `buckets.py`) picks `"bucket_0"`, `"bucket_1"` with no spec backing.
- **Classification:** `compounded` — leaf-02's contract on bucket_id format is derived entirely from leaf-01's undocumented inference, not from a spec line or contract symbol. The two leaves are now coupled through an inferred value that appears in no ground-truth source.
- **Conflicts with:** The spec (`feature-aggregator.md`) acceptance criteria make no mention of bucket label format. `AggregatedRow.bucket_id: str` gives only the type, not the value. Leaf-02 is told to "use whatever buckets.py returns" — which is the right policy — but the test written for leaf-02 must independently assume a format to assert against. If that assumption differs from leaf-01's choice, the test will fail for the wrong reason.
- **Damage assessment:** Low probability of actual breakage if leaf-01 and leaf-02 are reviewed together, but the chain of inference is opaque. If leaf-01 is revised (e.g., to use timestamp ranges as bucket_id), leaf-02's test breaks silently. The parent's assumption-sweep cannot catch this at merge time unless leaf-01.ASSUMPTIONS.md and leaf-02.ASSUMPTIONS.md are cross-checked.
- **Patch suggestion (no redo):** Add a note to the shared type contract or a parent-owned fixture that pins the bucket_id format (e.g., a constant like `BUCKET_LABEL_FORMAT = "bucket_{n}"`). Both leaves import from there. Alternatively, add a spec line explicitly prescribing the format before leaf agents are spawned.

---

### [eval-C / Assumption — spec accepted at Step 2 before bible check completes]

- **Assumption (ASSUMPTIONS.md):** `strategy_doc_path` was accepted from the task prompt as the bible. The spec was confirmed present. `NOTE: Procedure halted at Step 2 (Spec Gate / Bible Check). See verdict.txt.`
- **Finding:** The skill correctly halted. The assumption itself is clean. However, the assumption log entry `out_of_scope: nothing explicitly excluded — source: task prompt silent on exclusions` is technically moot (the halt preceded any decomposition), but if this log were read by a downstream agent resuming from a checkpoint, that entry could be misread as "the spec was validated and decomposition may proceed."
- **Classification:** `compounded` (mild) — the `out_of_scope` entry is justified by task-prompt silence rather than any spec line. It implies a pass that never occurred. The rest of the halt is correct.
- **Conflicts with:** `eval-C/inputs/docs/strategy.md` — "All aggregation, rollup, and analytical query logic lives in the data warehouse as SQL. We do NOT use Python pandas, Polars, or any other in-process DataFrame library." The wave-2 spec explicitly uses pandas, pd.read_sql, df.groupby, and df.resample — all explicitly anti-patterned.
- **Damage assessment:** The skill behavior is correct (HALT issued). The flag is on the assumption log entry only: if a resuming agent reads `out_of_scope: nothing explicitly excluded` and interprets it as a clean gate passage, it may proceed to decompose the uncorrected spec. Low risk if the verdict.txt is always read alongside, but the log entry should clarify "scope assessment is void — halt was issued before scope determination."
- **Patch suggestion (no redo):** Append to the `out_of_scope` assumption entry: "— VOID: halt issued at Step 2 before scope assessment completed. Do not use this entry as a gate-pass signal." No code changes needed.

---

## Unflagged entries

**eval-A:**
- Briefs directory inferred from task prompt, consistent with `.tdd-cascade.toml` — clean
- Multi-wave audit applied correctly — clean
- Fresh emission treatment (no prior FAIL history) — clean
- All 14 non-leaf-09 contract_imports resolve to known types.py symbols — clean
- All 15 budgets within max_impl_lines=200 and max_test_assertions=20 — clean

**eval-B:**
- spec_file path — confirmed present in workspace
- wave: 1 from spec front-matter — clean
- expected_leaf_count: 2 — matches module layout (buckets.py + sliding.py; integration tests parent-owned per toml) — clean
- strategy_doc_path: none identified — correctly recorded as missing rather than fabricated — clean
- out_of_scope: persistence, concurrency, cache invalidation — matches spec "Out of scope" section — clean
- umbrella_test_cmd from toml, deferred-RED correctly recorded — clean
- leaf-01 contract_imports: WindowSpec only (not AggregatedRow) — correct; buckets.py boundary computation does not construct AggregatedRow — clean
- No impl files written (verdict: CORRECT DECOMPOSITION) — clean

**eval-C:**
- spec_file, wave, expected_leaf_count, strategy_doc_path — all sourced from explicit task prompt — clean
- strategy_changes_since_last: unknown — correctly recorded, not fabricated — clean
- brief_reviewer: /tdd-review only — correct default — clean
- Halt at Step 2 with full conflict quotation — clean and correct behavior

**eval-D:**
- Leaf scope inferred from diff file paths — accurate for all 5 merges — clean
- Multi-merge sequential cascade identified correctly — clean
- merge-3 revert inference: merge-4 BEFORE matches merge-2 AFTER (not merge-3 AFTER), confirming revert — assumption is accurate and verifiable from input files — clean
- Parent assumption-sweep unknown: correctly flagged as "noted" rather than fabricated — clean
- Expected umbrella delta inferred from BEFORE/AFTER files rather than user-provided — correct non-interactive policy — clean

**eval-D edge observation (not flagged):** merge-5 AFTER shows "window slide produces buckets" still failing (1 remaining failure). The skill correctly recorded the delta (7 passes after merge-5 adding dashboard), but "window slide" was never re-introduced after the merge-3 revert. This is not an assumption error — it is an accurate read of the inputs — but it signals an incomplete cascade (window slide leaf needs a redo after the revert). The skill correctly did not fabricate a passing state.
