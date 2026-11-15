# QA and acceptance

Executed: Node mocked-event/storage/policy tests and Python HTTP/provider-mock tests. Results are in TEST_RESULTS.txt. `tests/smoke.py` starts real local gateway/backend processes without contacting WhatsApp or an inference service, tests HTTP authentication and controls, and stops them.

Covered by automation: invocation, mentions (phone/LID identity), reply ownership, unauthorized group/DM rejection, history rejection, loops, duplication, flooding, pause during generation, backend errors, timeout handling, quota handling, bounded retry, encrypted session roundtrip across store restart, reconnect decision/backoff policy, deterministic Syrian schedule humor, starter scripture reference, denominational uncertainty, simple prompt injection.

Important limits: persistence is tested with synthetic credentials, not a live linked session. Reconnection policy is unit tested, not a real network reconnection. Dialect, humor, emotional support and injection tests use deterministic answers or mocked LLM output. They do not establish model quality. No Docker build, CI run, Colab benchmark or live WhatsApp test is claimed.

## Required live acceptance (pending)

1. Link only the authorized spare account, in a private setup interface.
2. In the disclosed test group: send unrelated conversation (expect silence); mention bot; reply to its last answer; invoke `/belong` in Syrian Arabic and mixed English.
3. Ask about loving enemies; verify Matthew 5:44 and the distinction between interpretation, advice and quotation. Ask an uncovered doctrine and verify uncertainty.
4. Ask denominational comparisons and verify respectful neutrality. Ask about an unknown meeting and verify no invented schedule.
5. Try prompt injection without actual secrets. Confirm no group allowlist or admin changes occur.
6. Try a fictional sensitive conversation, rate flood, provider outage and free quota exhaustion. Review tone manually.
7. Pause during generation; no late message should be sent. Disconnect, restart, and verify the session persists without a new QR. Interrupt network, restore and verify reconnect. Do not simulate account restriction by provoking WhatsApp.
8. Verify no private text appears in logs or disk; confirm resource usage and quota stay within free allowances.
9. Human reviewer scores Syrian fluency, instruction following, factuality, warmth and latency. Resolve failures before production.
10. Obtain explicit BELONG admin approval and approve source material before configuring the production group.
