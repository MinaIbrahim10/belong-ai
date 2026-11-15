# Privacy and security

Accepted text is sent to the configured inference provider; this changes the privacy boundary from WhatsApp end-to-end encryption to that provider's processing. Tell test members and leadership before activation. Unrelated messages never reach inference. Do not represent group conversations as confidential counselling.

No message bodies, phone numbers, participant names, JIDs or API responses are logged. Structured logs contain only fixed event names and timestamps. Baileys protocol logging and Uvicorn access logs are disabled. JIDs appear only transiently and in private configuration/auth state where required by the protocol. A one-way message-ID hash remains up to 24 hours; bot-reply tracking hashes remain 10 minutes. Cleanup runs every minute while the gateway is running, and on the next accepted event. Stopped disks retain expired hashes until the process resumes; they contain no chat text.

Session state is AES-GCM encrypted. The encryption key resides in a mode-600 host environment file, not inside the database. Protect the host as well: encryption does not defeat a compromised running process. QR material exists briefly in process memory; private QR export must be deleted. No OTP collection is implemented.

Do not enable public ingress to management/backend. Use distinct long admin and inter-component tokens. Docker runs without Linux capabilities and with read-only root filesystems. A writable private volume holds state. Runtime code has no shell/tools interface accessible to the LLM. Prompt injection cannot change allowlists or execute admin actions, which are enforced outside the LLM.

Content safeguards are incomplete: keyword classification and quotation filters do not establish semantic correctness. Prompt injection defenses and sensitive-topic tone require real model adversarial evaluation. This prototype is not ready for unsupervised production counselling or theological advice.
