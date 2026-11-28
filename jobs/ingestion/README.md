# jobs/ingestion (M6i)

Turns the scouts' JSON-lines files into idea cards, stores them in PostgreSQL, embeds their chunks into Qdrant and
writes a snapshot. Running it again adds nothing.

| Step | File |
|---|---|
| items to cards, duplicates dropped by address and content | `scd_ingestion/cards.py` |
| chunks of up to 800 characters, ids `<card_id>#c<n>` | `scd_ingestion/chunks.py` |
| embedding, `BAAI/bge-small-en-v1.5` (384), baked into the image | `scd_ingestion/embed.py` |
| Qdrant collection `chunks`, cosine | `scd_ingestion/index.py` |
| tables `cards`, `card_sources`, `ingestion_runs` | `scd_ingestion/store.py` |

| Setting | Meaning |
|---|---|
| `DATABASE_URL`, or `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DB` | required; without them the job does nothing |
| `SCOUT_OUT` | input folder, default `/data/raw` |
| `SNAPSHOT` | snapshot file; keep it out of the input folder's `*.jsonl` (a subfolder) |
| `VECTOR_STORE_URL` | default `http://qdrant:6333` |

```sh
python -m scd_ingestion.job                          # ingest
python -m scd_ingestion.job --restore cards.jsonl    # rebuild store and index from a snapshot, offline
python -m pytest jobs/ingestion -q                   # from the repository root
```

Cards hold only what the source gave: `problem` and `customer` are empty, `stage` is `unknown`, `funding_usd` is
null. Niche tags come from source topics only. The scheduled CronJob in `k8s/` does not pass these settings yet; the
run of record used `docs/evidence/phase4/ingestion-job.yaml`.
