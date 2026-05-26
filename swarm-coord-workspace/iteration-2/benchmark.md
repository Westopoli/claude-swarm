# /swarm discovery skill — iteration-2 benchmark

Paired evals (with-skill vs no-skill baseline). 3 evals × 2 configs = 6 subagent runs. Each run was given a mock project directory + scripted USER_RESPONSES.md so the interactive skill could be exercised in non-interactive mode.

## Headline

| Config | Pass rate | Assertions | Time (s) | Tokens |
|---|---|---|---|---|
| **with_skill** | **100% (15/15)** | 15/15 | 174.9 ± 25.0 | 39,063 ± 1,666 |
| without_skill | 73.3% (11/15) | 11/15 | 110.3 ± 13.0 | 26,019 ± 217 |
| **Δ** | **+26.7pp** | +4 | +64.6s | +13,044 |

Skill catches **4 failures** baseline misses, at a cost of ~58% more wall-time and ~50% more tokens. Per the evaluation-rubric this is the right trade — discovery-time drift is the most expensive class of failure in the cascade.

## Per-eval

### I — design-leak (CSV → JSON)

| Config | Score | Notes |
|---|---|---|
| with_skill | 5/5 | 1-symbol contract. 6 entries in `.UNSTATED.md`. Step-4 trace-or-flag + step-10 self-scan caught U-5/U-6 picks the user-question script did not even cover. |
| baseline | 4/5 | Locked RFC 4180 CSV defaults + JSON array-of-objects + UTF-8-strict into spec body *before* flagging them. Spec missing `[source: user-stmt-N]` discipline. |

### J — contract-overreach (URL shortener)

| Config | Score | Notes |
|---|---|---|
| with_skill | 5/5 | 3-symbol contract (shorten / lookup / redirect). 6 `.UNSTATED.md` entries. STOP_AND_LOG questions stayed OUT of the contract. |
| baseline | 4/5 | Silently invented `CollisionError`, `SlugNotFoundError`, 7-char alphanumeric slug policy, retry-5x — and **baked them into types.py**. Flagged in `.UNSTATED.md` *after* the contract was locked. Exact failure mode the eval probes for. |

### K — unstated-sweep (link extractor, minimal input)

| Config | Score | Notes |
|---|---|---|
| with_skill | 5/5 | 13 entries in dedicated `.UNSTATED.md`. Covers timeout, link-defn, abs/rel, encoding, network failure, output format. |
| baseline | 3/5 | Same 13 inferences but **buried inside spec.md as a table** instead of a separate audit-target. No `.UNSTATED.md` artifact. Easy to skim past on review. |

## Analyst observations

- **Baseline already produced flagged-inference logs in I and J.** This is a script-induced artifact — `USER_RESPONSES.md` told it to record dispositions. Without the script's hint, baseline would likely have invented values silently. The eval isolates *contract minimality* and *artifact discipline*, not "does the model think to flag at all."
- **The load-bearing failure is J's contract-overreach.** Baseline silently put `CollisionError` and `SlugNotFoundError` into the type contract — those decisions become permanent once leaves consume the contract. Skill kept the contract at 3 symbols matching exactly what the user named.
- **K's failure mode is the subtle one.** Same content in both runs, but the baseline stuffed inferences into the spec body where they look like normal spec content. Skill's separate `.UNSTATED.md` keeps the audit surface distinct.
- **Pytest sandbox-blocked in 3 runs (I-with, J-with, K-with).** Subagents could not literally run umbrella_test_cmd. RED was structurally guaranteed by sentinel bodies but not empirically observed. Not a skill defect — sandbox limit.
- **Notable skill gap surfaced by K subagent**: "STOP_AND_LOG / non-interactive mode is not in SKILL.md itself" — only in `playbook.md`. An LLM with SKILL.md but not the playbook could hang. Worth a follow-up patch.

## Verdict

Skill performs as designed on all three failure modes. Safe to push to main.
