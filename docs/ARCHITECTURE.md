# Architecture

One persistent Node gateway receives live WhatsApp events. An allowlist/trigger/age gate runs before the text is sent to FastAPI. Durable hashed deduplication suppresses repeat events. User, group and total request caps run before inference. One inference job is accepted at a time per connection; work while busy is dropped rather than queued.

FastAPI authenticates the gateway with a separate bearer token. It first selects exact, curated topic answers. Missing recognized religious topics receive an uncertainty response. Ordinary conversation uses a configurable OpenAI-compatible endpoint or Cloudflare Workers AI. Output is length limited; obvious generated scripture references and quotations are rejected. This is a conservative heuristic, not a proof against all hallucinations or adversarial prompts.

The gateway stores encrypted Baileys authentication values in SQLite with AES-256-GCM, random nonces and a separate 256-bit environment key. Transactions group Signal key writes. The database also holds hashed event IDs (24 hours), hashed bot output IDs (10 minutes), and pause state. A periodic cleanup runs every minute. Chat text is never stored.

The management interface is on localhost, authenticated separately. `/pause` stops responses including in-flight results; `/resume` requires a configured group; `/disconnect` closes the socket and requires a restart. SIGTERM closes the process. WhatsApp Linked devices can revoke credentials independently.

Reconnection uses bounded exponential delay; logout, forbidden, replaced-session and known invalid-session states stop and require operator review. No retries circumvent a restriction. Sending is not retried because delivery ambiguity can duplicate messages.

The protocol adapter is isolated in `whatsapp-gateway/src.js`; pure message decisions and handling have independent tests. Replacement with a future official existing-group API does not require rewriting the backend.

The theology preferences file records proposed denomination/leadership approval metadata. It does not automatically change doctrine; approved content and prompt edits are reviewed in Git. Runtime web research is deliberately disabled.
