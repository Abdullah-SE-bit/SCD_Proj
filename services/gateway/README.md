# services/gateway (M1)

Public API. **Walking skeleton: fixture data only** (P01.03). No login, rate limits or live progress yet, and the
orchestrator is not called. Contract: `contracts/openapi/gateway.json`.

| Route | Behaviour |
|---|---|
| `POST /validate` | body `{"idea": "..."}` (1 to 2000 characters) returns `{"run_id": "fixture-run"}`; else 400 |
| `GET /runs/fixture-run` | `run_id`, `status`, `label` (`FIXTURE DATA`) and a fixed `verdict`; other ids 404 |
| `GET /health`, `/ready`, `/info` | probes, from `scd_gateway/base.py` |

The idea text is checked and then ignored: every idea gets the same verdict. Listens on `PORT` (default 8000).

```sh
python -m pytest services/gateway -q
```
