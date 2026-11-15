# Deployment and administration

## Current status

No VM/account credentials are connected. No public endpoint, live LLM, WhatsApp session, or group is active. GitHub repository creation requires browser sign-in. Do not equate workspace process smoke tests with deployment.

## Zero-cost candidate

An existing, eligible Oracle Always Free VM with persistent block storage can run both containers, using hosted inference. Account eligibility in Syria and actual spare capacity are unverified. Signup asks for card verification, potentially a temporary authorization hold. Do not start signup or upgrade to paid automatically. No claim of guaranteed free 24/7 availability: idle instances can be reclaimed.

Choose only resources explicitly marked Always Free in the authenticated console, review the current total resource allocation, and remain on the free account. Never substitute a trial resource. For this lightweight gateway/backend, start with 1 GB RAM only if measured usage permits; 2 GB is more comfortable. Do not host a 4B model in 1 GB RAM.

## Host setup

1. Create a **private** repository `belong-ai` after GitHub sign-in; push this source and lockfile. Keep Actions within the account's included quota and do not enable paid overages.
2. Obtain an eligible always-free VM with the provider's private console or SSH access. Install Docker/Compose from official sources. Keep ingress closed except authenticated administration; outbound HTTPS/WebSockets are required.
3. Clone the private source on that host. Run `python deployment/init-secrets.py` once. It creates a mode-600 `.env` without displaying keys.
4. Create/use Cloudflare Workers **Free**, without paid billing or prepaid AI credits. Put an appropriately scoped Workers AI token and account ID only into the host's private `.env`. Set `LLM_PROVIDER=cloudflare`. The proposed model is `@cf/qwen/qwen3.8-27b`; quality and real quota behavior remain to be tested. Do not auto-fallback to paid services.
5. Have the user create a separate WhatsApp test group, explain the AI/provider processing, and manually add the test account. Configure its exact group JID privately as `TEST_GROUP_IDS`. An invite code is NOT a JID. Group-ID discovery is provided via the private opt-in setup procedure below.
6. Set `CONNECT_WHATSAPP=true`, leave production IDs empty, and run `docker compose up -d --build`.
7. On a private host console, use `python deployment/admin.py qr`, privately display `/tmp/belong-link.png`, scan through WhatsApp > Linked devices > Link a device. Delete the PNG immediately. Do not upload/screenshot the QR into chat, notebook outputs, GitHub, or logs.
8. Resume with `python deployment/admin.py resume`. Run the manual acceptance suite in QA.md. Restart containers and verify linking persists. No live success may be claimed before this.

## Test group identifier

While paused and linked, run `python deployment/admin.py enroll` in the private console. It returns a random, five-minute setup code (not a WhatsApp login credential). From another consenting account in the **test group only**, send `/belong enroll <code>`. The bot captures only the group ID of that exact matching fresh message and does not reply. Other group text is discarded. Run `python deployment/admin.py enrollment` privately to read the captured ID; put it in `.env` as TEST_GROUP_IDS and restart the gateway. Enrollment never auto-adds a group to the allowlist. Delete the test setup message/code afterwards. Never put the code or group ID in GitHub or this chat.

## Administration

`python deployment/admin.py pause` pauses persistently.
`python deployment/admin.py resume` resumes permitted groups.
`python deployment/admin.py disconnect` closes WhatsApp until restart.
`docker compose stop gateway` is an independent emergency shutdown.
WhatsApp > Linked devices > select the bot > Log out revokes the session.

To unlink permanently, stop the gateway, revoke on the phone, and remove its private state volume only with the operator's explicit intent. Do not print its contents. Backups, if any, must be encrypted and kept separately from SESSION_KEY.

Production: obtain explicit BELONG administrator approval and announce the bot/provider behavior to members. Review theology sources and personality with leadership. Then, privately add only the approved group JID and set PRODUCTION_APPROVED=true. Production remains disabled in the delivered configuration.
