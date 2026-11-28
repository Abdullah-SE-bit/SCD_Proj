# services/tools (M5)

The only module with internet access (NetworkPolicy `allow-tools-internet`).

- `POST /fetch` `{url, method?, payload?}`: HTTPS to allow-listed domains on public addresses, redirects re-checked,
  robots.txt where it applies, minimum interval and back-off per domain, cache, sanitiser. Answers 403 refused,
  429 rate limited, 502 source failed. Fields: `content`, `content_type`, `removed_instructions`, `cached`,
  `retrieved_at`.
- `POST /llm` `{messages, max_tokens?, temperature?, json?, run_id?}`: the hosted model (Groq free tier) with a token
  budget per run and per day. 503 when no key and model are configured.

Source register with the permission basis of each domain: `scd_tools/sources.json`. External keys come from the
Secret `api-keys` (`scripts/load_secrets.sh` reads them from `.env`); they are sent only to their own domain.

Limits: rate limits, cache and budgets are in memory; the sanitiser matches known phrasings only.

Run from this directory: `python -m scd_tools.app`. Tests: `pytest services/tools tests/security`.
