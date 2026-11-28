# services/scouts (M4)

Brings in new data from Hacker News, GitHub and Product Hunt. Every request goes through M5 (`TOOLS_URL`, default
`http://tools:8000`); the scouts have no internet access and hold no keys.

- On demand: `POST /scout` `{source, limit?, query?}` returns `items` (and `error` when a source fails part way).
- Scheduled: CronJob `scouts` runs `python -m scd_scouts.run`, one JSON-lines file per source into `/data/raw`
  (volume `raw-items`). One failing source does not stop the others.

Item fields: `source`, `external_id`, `url`, `title`, `text`, `created_at`, `signals`, `retrieved_at`. No author names.

Product Hunt needs `PRODUCT_HUNT_TOKEN` in the `api-keys` Secret; without it that source reports its error.
GitHub is paced for the unauthenticated limit (`GITHUB_PAUSE_SECONDS`, default 6.5).

Tests: `pytest services/scouts`.
