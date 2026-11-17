# Live status, 2026-11-17

WhatsApp linked successfully in an authorized test group. User confirmed both a sourced reply and a live Cloudflare-generated conversational reply. Runtime is GitHub Codespaces, subject to its included quota and automatic stops. Cloudflare credentials and encrypted WhatsApp state remain private on that runtime.

This update replaces canned theological replies with source retrieval and generation. It recognizes explicit references for 66 books, fetches only validated ebible.org WEB chapter URLs, and asks the model to select at most two passages for general religious questions. It verifies verse existence and appends source links on the server. Verse existence is not proof of theological entailment. Denominational documents and deuterocanonical books are not yet included. Leadership should review the output and approve additional sources.

Conversation context is in RAM only, scoped to a hashed group/member pair, up to two turns for five minutes, capped at 200 conversations. Expired contexts are cleared during processing. No history is ingested. Scripture cache contains only public source text.

Administrator approval to add the bot to BELONG was reported by the user. The production group has not yet been enrolled or activated. Test the updated responses before enrollment.
