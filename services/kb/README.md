# services/kb (M6)

Searches the idea cards the ingestion job stored. Contract: `contracts/openapi/kb.json`.

| Route | Behaviour |
|---|---|
| `POST /search` | `{"query", "filters"?}` returns up to 10 evidence items, best first; empty list when nothing matches; 400, 503 |
| `GET /coverage` | cards and chunks by source, oldest and newest publication date, last retrieval, niche counts |

Filters: `date_from`, `date_to` (`YYYY-MM-DD`, publication date, else retrieval date), `source`, `niche`.

How it ranks: BM25 words and bge-small vectors (Qdrant) are fused by rank, the best 30 are reranked by the
`ms-marco-MiniLM-L-6-v2` cross-encoder. Each item's `evidence_id` is `<card_id>#c<n>` and its card exists in
PostgreSQL. Quotes are retrieved text: data, never instructions.

Settings: `DATABASE_URL` or `POSTGRES_*` (without them both routes answer 503), `VECTOR_STORE_URL`. Needs about
1 GiB of memory and the models baked into the image. The chunk list is held in memory and refreshed every 5 minutes.

```sh
python -m pytest services/kb -q    # from the repository root
```

Ranking quality is not measured yet (P04.05). `k8s/` does not give this service its database settings or enough
memory; the demonstration used `docs/evidence/phase4/kb-pod.yaml`.
