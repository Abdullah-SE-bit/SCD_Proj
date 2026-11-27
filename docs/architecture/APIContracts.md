# API contracts

Machine-readable: `contracts/openapi/*.json` (7 documents) and `contracts/schemas/*.schema.json` (10 schemas,
each with a valid and an invalid example). Checked by `contract-tests`.

Only documented capabilities exist. Request or response bodies the course documents do not specify are open
objects marked `x-status: proposed`; the owning task fixes them by PR, updating both sides.

| Service | Endpoints |
|---|---|
| gateway (public) | POST /auth/register, /auth/login; GET, PUT /profile; POST /discover, /validate; GET /runs/{id}, /runs/{id}/events; POST /runs/{id}/answer, /approve; POST /ideas/{id}/challenge, /whatif; GET /ideas, /ideas/{id}/versions, /compare, /metrics |
| tools (M5) | POST /fetch |
| kb (M6) | POST /search |
| scorer (M10) | POST /score |
| verdict (M11) | POST /verdict, /whatif |
| critic (M12) | POST /check |
| agentops (M13) | POST /trace; GET /runs/{id}/trace |

## Authentication
Only the public gateway requires a user token. Internal services accept in-cluster calls only, restricted by
NetworkPolicy (see Architecture); their documents declare no user authentication.

## Health convention
`/health`: 200 when the process is alive, no dependency checks. `/ready`: 200 only when it can serve now
(database, vector store, model loaded as applicable), else 503.

## Change rules
A contract change is its own PR, labelled `CONTRACT_UPDATED` in the session message, reviewed by the other
contributor, with examples updated.
