# Scripted user responses for eval J-contract-overreach

You are running in NON-INTERACTIVE mode. Real user is not present. Treat this file as the canonical user-response transcript. When the skill prompts a question, look up the matching response below. If the response is `STOP_AND_LOG`, treat the question as one the user cannot answer right now — proceed under the playbook's non-interactive mode (record an inference in `.UNSTATED.md`) instead of hanging.

---

## Q (intake, "What do you want to build?")
A: A simple URL shortener. The user submits a long URL and gets back a short slug. Visiting the short slug redirects to the long URL. That's it.

## Q (intake, "Do you already have any documentation?")
A: No.

## Q (restate-and-confirm, step 2)
A: Approve.

## Q (architecture intake — inputs)
A: A long URL string from the user.

## Q (architecture intake — outputs)
A: A short slug string. And a redirect (HTTP 302) when the slug is visited.

## Q (architecture intake — main behaviors / transformations)
A: 1) shorten(long_url) -> slug. 2) lookup(slug) -> long_url. The redirect handler uses lookup under the hood.

## Q (architecture intake — explicit constraints)
A: Python 3.11+. Use whatever simple in-process storage is appropriate for the umbrella to be runnable in tests.

## Q (architecture intake — out of scope)
A: Persistence across process restart. User accounts. Analytics. Rate limiting. Slug expiry. Custom slugs.

## Q (architecture intake — what does "done" look like for the umbrella)
A: shorten() returns a slug. lookup() on that slug returns the original URL. Visiting the slug returns 302 with Location header equal to the original URL.

## Q (architecture intake — slug length / charset / collision policy)
A: STOP_AND_LOG

## Q (architecture intake — what happens on lookup miss)
A: STOP_AND_LOG

## Q (architecture intake — anything about authentication, rate limits, expiry, analytics)
A: Out of scope. Do not include in the contract.

## Q (spec review gate)
A: Approve.

## Q (contract review gate)
A: Approve.

## Q (umbrella review gate)
A: Approve.

## Q (.UNSTATED.md dispositions, any entry)
A: accept-as-flagged

## Q (anything not covered above)
A: STOP_AND_LOG
