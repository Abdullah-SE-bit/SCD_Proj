# Database entities and migration specification

Status: the application tables (`users` to `conversations`) exist as migrations in
`services/profile/scd_profile/migrations/` (P02.01). The knowledge tables arrive with P04.03.
Added beyond the documented columns: text ids, `idea_versions.id`, `verdicts.id`, `verdicts.document`,
`profiles.version` and decision and creation times.
Columns are the documented minimum (Guide Figure 1). Types and constraints are proposals.

| Table | Documented columns | Proposed keys and constraints |
|---|---|---|
| users | id, email, hash, created_at | pk id; unique email |
| profiles | user_id, skills, hours, team, goal | fk user; add weeks_available, compute, interests, version (Guide 2.1, cache key) |
| ideas | id, user_id, title, source (own/generated) | check source |
| idea_versions | idea_id, version, text, created_at | unique (idea_id, version) |
| verdicts | version_id, verdict, score, confidence | check verdict enum; store full verdict JSON |
| dimension_scores | verdict_id, dimension, score, conf, evidence | unique (verdict_id, dimension) |
| approvals | run_id, action, decision | |
| traces_index | run_id, cost, latency, status | pk run_id |
| conversations | idea_id, turns | |
| cards | id, name, one_liner, problem, customer, niche | add remaining card schema fields (Guide 2.1) |
| card_sources | card_id, platform, url, fetched_at | unique url |
| niches | id, name, size, trend_slope | |
| niche_stats | niche_id, month, launches, mentions | unique (niche_id, month) |
| ingestion_runs | run_id, source, added, dropped | |
| vector store | chunk_id, card_id, embedding, date | payload filters: date, source, niche |

Migrations: forward-only files applied by one command (`python -m scd_profile.migrate`) on an empty database,
tested in CI on SQLite and locally on PostgreSQL; never edit an applied migration.

Note: the figure names the column `one_liner` while the card schema calls it `summary`; map one to the other.
