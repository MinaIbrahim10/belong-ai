# Verified research — 2026-11-15

## WhatsApp

Meta Groups API documentation now describes Official Business Account eligibility, API-created invite-only groups and an eight-participant limit. The documented creation/invite flow offers no bridge for joining an existing consumer-created BELONG group. Therefore no supported route satisfying this requirement was found; do not claim that all WhatsApp group APIs are absent.

Sources: https://developers.facebook.com/documentation/business-messaging/whatsapp/groups and /groups/get-started

Baileys uses linked-device connectivity and is unofficial. Installed npm version: `@whiskeysockets/baileys@7.0.0-rc14`, pinned with lockfile, running under Node 24. It is a release candidate, so live compatibility is unverified. The upstream documentation advises a custom production auth store; this project implements encrypted SQLite rather than demo multi-file auth.
Sources: https://baileys.wiki/ ; https://github.com/WhiskeySockets/baileys.wiki-site/blob/main/docs/intro.md

## Hosting comparison

| Service | Persistent gateway | Private durable session | Free constraints | Decision |
|---|---|---|---|---|
| Oracle Always Free VM | Technically suitable | Block storage | Card verification, capacity, eligibility, idle reclamation | Conditional first choice; no account provisioned |
| Render Free web | Sleeps after inactivity | No free persistent disk | Not guaranteed continuous; ephemeral local state | Reject for permanent gateway |
| Cloudflare Workers | Request-driven runtime, not a conventional Node daemon | Requires external state design | Worker resource limits; no tested Baileys port | Use AI API, not this gateway |
| Hugging Face CPU Basic Space | Can run process while awake | Default filesystem ephemeral | Free CPU Spaces sleep after 48h inactivity | Experiments only, not permanent gateway |
| Google Colab | Interactive temporary runtime | Session state unsafe in notebook outputs | Quotas and disconnections | Model experiments only |

Oracle current docs list A1 allowance equivalent to 2 OCPU / 12 GB and 200 GB block storage; check the actual tenancy before allocating anything. No inference about the user's eligibility is made from these general limits. Regional eligibility for each hosting/inference service remains unverified until authorized account setup. No paid account, card, trial, or artificial keep-alive is used.

Sources:
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- https://www.oracle.com/cloud/free/faq/
- https://render.com/docs/free
- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/workers/runtime-apis/websockets/
- https://huggingface.co/docs/hub/spaces-gpus

## Model assessment (not benchmark results)

| Candidate | Weight-only memory estimate | Expected tradeoff | Measured Arabic/latency |
|---|---|---|---|
| Qwen3 1.7B | FP16 ~3.4 GB; raw 4-bit ~0.85 GB | Lowest memory; less capacity for instruction/reasoning | Not measured |
| Qwen3 4B | FP16 ~8 GB; raw 4-bit ~2 GB | More capacity, more RAM/latency | Not measured |
| Hosted Qwen3.8 27B | No local weights | Larger hosted alternative, finite free quota | Not measured |

These are arithmetic weight-only estimates; quantization metadata, KV cache and runtime increase RAM. No claim that advertised multilingual support establishes Syrian dialect quality. Both Qwen3 cards advertise multilingual capabilities; use the supplied benchmark harness and a Syrian human reviewer before selection.

Cloudflare Workers Free includes 10,000 neurons/day, with failure at the free cap rather than automatic paid overage unless the account is upgraded. Qwen3.8-27b is listed in the current catalog and not among models requiring a paid billing method on the checked pricing page. Qwen3-30b-a3b-fp8 is scheduled for retirement on 2026-11-20, so it is not the new deployment default. Model availability and quota must still be verified in the actual account.

Sources:
- https://huggingface.co/Qwen/Qwen3-1.7B
- https://huggingface.co/Qwen/Qwen3-4B
- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://developers.cloudflare.com/workers-ai/models/qwen3.8-27b/
- https://developers.cloudflare.com/workers-ai/models/qwen3-30b-a3b-fp8/

## Scripture and rights

Two starter entries are original Arabic paraphrases of Matthew 5:44 and James 1:19–20, with interpretation/personal advice labeled. The source is the public-domain World English Bible. No copyrighted Arabic translation is copied. They are technically reviewed starter entries, **not yet approved by BELONG leadership**. Other religious topics use an uncertainty fallback. This is a small curated foundation, not a comprehensive theological corpus.

Sources: https://ebible.org/eng-web/copyright.htm ; https://ebible.org/eng-web/MAT05.htm ; https://ebible.org/eng-web/JAS01.htm
