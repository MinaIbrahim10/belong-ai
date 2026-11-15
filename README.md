# BELONG AI

Working source prototype for an existing WhatsApp youth group. **Not deployed or linked yet.**
No charges incurred. No production group was joined or contacted.

Node 24 + Baileys 7.0.0-rc14 gateway; FastAPI backend; encrypted SQLite linked-device state; curated Arabic answers; configurable hosted inference.

## Safety defaults

- WhatsApp connection disabled, replies paused, group allowlist empty.
- Production IDs ignored unless `PRODUCTION_APPROVED=true` after explicit administrator approval.
- Only `/belong`, verified mentions, or replies to a recently sent bot message trigger processing.
- No conversation archive, history sync, media handling, view-once decoding, automatic invitations or group joining.
- No chat memory: each accepted text is ephemeral. This intentionally sacrifices conversational continuity.
- Baileys is unofficial: account restriction, logout and protocol breakage remain possible.

## Run tests

```sh
npm ci --prefix whatsapp-gateway
npm test --prefix whatsapp-gateway
python -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
python -m pytest -q tests
python tests/smoke.py
```

## Start on an authorized free VM

```sh
python deployment/init-secrets.py
# Privately edit .env: provider, allowed TEST_GROUP_IDS, CONNECT_WHATSAPP=true.
docker compose up -d --build
python deployment/admin.py qr
# Privately view /tmp/belong-link.png; scan from WhatsApp Linked devices. Delete the PNG.
python deployment/admin.py resume
```

Keep HTTP management bound to host loopback. Use authenticated SSH port forwarding or the provider's private console; never publish port 8080. Never paste a QR, session file, OTP or token in chat/GitHub.

See [deployment](docs/DEPLOYMENT.md), [architecture](docs/ARCHITECTURE.md), [privacy](docs/PRIVACY.md), [research](docs/RESEARCH.md), [QA](docs/QA.md) and [troubleshooting](docs/TROUBLESHOOTING.md).
