# Troubleshooting

- No replies: check `/healthz`, pause state, exact allowlist JID, trigger and message age. Fresh bot starts paused. Unrelated, old, media, disappearing and view-once content is intentionally ignored.
- Replies to old bot messages fail: bot output IDs expire after 10 minutes; use a mention or `/belong`.
- QR 404: no pending QR yet, or already linked; check connected status privately. Do not enable verbose protocol logs.
- Logged out/restricted/replaced: gateway stops retries. Review WhatsApp on the phone. Do not bypass challenges or repeatedly re-register.
- Lost session after restart: verify the same persistent volume and SESSION_KEY. A different key cannot decrypt the state. Never upload the database for diagnosis.
- AI unavailable: verify free-tier quota, provider credential and current model ID in the provider dashboard. Failures return a brief safe answer; no paid fallback exists.
- Theology answer unavailable: add reviewed content with source/rights metadata; do not remove the uncertainty fallback merely to appear knowledgeable.
- Render sleeping: not a code bug. Use a suitable persistent host; no synthetic keep-alive.
- Docker unavailable in this workspace: native process smoke tests can run, but container builds remain unverified until Docker is available.
