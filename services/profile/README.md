# services/profile (M2)

Application records in PostgreSQL. **So far** (P02.01): tables, migrations, repositories and services. The service
still exposes only `/health`, `/ready` and `/info`; account and profile routes arrive with P02.02.

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
