# services/gateway (M1)

Public API. Contract: `contracts/openapi/gateway.json`.

| Route | Behaviour |
|---|---|
| `POST /auth/register` | `{"email", "password"}` returns `user_id` (201); 400, 409, 429 |
| `POST /auth/login` | same body, returns `{"token"}`; 401 for a wrong email or password; 429 |
| `GET`, `PUT /profile` | needs `Authorization: Bearer <token>`; own profile only (401, 403) |
| `POST /validate`, `GET /runs/fixture-run` | walking skeleton: one fixed verdict marked `FIXTURE DATA`, no login |
| `GET /health`, `/ready`, `/info` | probes |

| Setting | Meaning |
|---|---|
| `PORT` | default 8000 |
| `PROFILE_URL` | default `http://profile:8000` |
| `JWT_SIGNING_KEY` | at least 32 characters; without it a temporary key is used and logins end at restart |

Limits per minute: 5 logins per email, 20 registrations in total, 60 validations in total. They are counted in
each process, and no client address is available, so one client can use up a shared limit. Tokens last 8 hours
and cannot be revoked.

```sh
python -m pytest services/gateway -q
```
