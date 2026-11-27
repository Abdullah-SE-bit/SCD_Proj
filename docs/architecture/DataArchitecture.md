# Data architecture

Proposed, from Guide Figure 1 and section 2. Entity and migration details: `contracts/database/entities.md`.

```mermaid
erDiagram
  users ||--|| profiles : has
  users ||--o{ ideas : owns
  ideas ||--o{ idea_versions : has
  idea_versions ||--o{ verdicts : judged
  verdicts ||--o{ dimension_scores : contains
  ideas ||--o| conversations : discusses
  traces_index ||--o{ approvals : "run_id"
  cards ||--o{ card_sources : from
  cards ||--o{ chunks : split
  niches ||--o{ cards : groups
  niches ||--o{ niche_stats : monthly
  ingestion_runs ||--o{ card_sources : records
```
`ingestion_runs → card_sources` is a proposed link; the source figure does not draw it.

| Store | Owner | Content |
|---|---|---|
| Postgres (application) | M2 | users, profiles, ideas, idea_versions, verdicts, dimension_scores, approvals, traces_index, conversations |
| Postgres (knowledge) | M6, M7 | cards, card_sources, niches, niche_stats, ingestion_runs |
| Vector store | M6 | chunk_id, card_id, embedding, date |
| Redis | M2 | cache entries only, with TTL (key: AMB-11) |
| Volumes | M13 | traces/*.jsonl, eval/results/*.json |
| Git | all | prompts/, rubrics/, config, labelled sets |

Rules: chunks keep card ids; every claim links to card ids; only public data; a card snapshot is kept.

## Ingestion pipeline
```mermaid
flowchart LR
  S[Scout via M5] --> C[Clean and sanitise] --> D[Dedupe by canonical URL and content hash]
  D --> I[Idea card validated against schema] --> K[Chunk, keep card_id] --> E[Embed] --> X[(Index)]
  I --> SN[Snapshot file]
  X --> R[Run record: added, dropped] --> DR[Drift report]
```
