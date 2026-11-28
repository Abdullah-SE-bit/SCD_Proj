# services/profile (M2)

Application records in PostgreSQL: tables, migrations, repositories, services and internal routes.

| Internal route | Behaviour |
|---|---|
| `POST /users` | register; password stored as a salted scrypt hash |
| `POST /sessions` | check email and password, return `user_id` |
| `GET`, `PUT /users/{user_id}/profile` | read or save the profile; each save raises its version |

They trust the caller: only the gateway authenticates users, and no ingress policy stops other pods.
History, comparison and the cache arrive with P02.03.

| Layer | File |
|---|---|
| routes | `scd_profile/app.py` |
| rules, validation, ownership | `scd_profile/services.py` |
| SQL | `scd_profile/repositories.py` |
| connection and transactions | `scd_profile/db.py` |

Settings: `DATABASE_URL`, or `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` and `POSTGRES_DB`.
With neither, the service starts without a database. With one, `/ready` is 503 until it answers.

```sh
python -m scd_profile.migrate      # bring an empty or older database to head
python -m pytest services/profile -q
```

The tests use SQLite. Set `TEST_DATABASE_URL` to a **throw-away** PostgreSQL database (its public schema is dropped)
and install `requirements.txt` to run them against PostgreSQL.


## History, comparison and cache (P02.03)
Internal routes under `/users/{user_id}`: `ideas` (POST, GET), `ideas/{id}/versions` (POST, GET),
`ideas/{id}/versions/{n}/verdict` (POST), `compare` (POST `{ideas: [a, b]}`),
`ideas/{id}/versions/{n}/cache` (PUT `{rubrics, engine, snapshot, verdict}`) and `.../cache/lookup` (POST).
`GET /metrics` counts cache hits, misses and errors; each hit is also logged. `REDIS_URL` turns the cache on; entries
expire after a day. Public through the gateway: `GET /ideas`, `/ideas/{id}/versions`, `/compare?a=&b=`, `/metrics`.

Not wired yet: the cluster passes no database or Redis address to this service and does not run the migrations.
