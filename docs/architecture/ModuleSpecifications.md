# Module specifications

Proposed. Every service exposes `/health` and `/ready`.

## M1 Web UI and API gateway
- **Units:** ui, gateway
- **Inputs:** browser requests
- **Outputs:** pages, SSE stream, JSON
- **Depends on:** M3, M2
- **API boundary:** public endpoints
- **Error handling:** validation errors, 401, 429
- **Authentication:** user login; rate limits
- **Data owned:** none (no state)
- **Observability:** request count, latency, 4xx/5xx
- **Security:** input validation; no model or scout calls from browser
- **Deployment:** Deployment, autoscaled, runtime API URL
- **Requirements:** M01-*, USR-003/006/010, API-003..006

## M2 Profile, session and cache
- **Units:** profile
- **Inputs:** profile, idea, version, run data
- **Outputs:** stored records, cache entries
- **Depends on:** Postgres, Redis
- **API boundary:** internal CRUD
- **Error handling:** fail closed on DB loss; cache miss on Redis loss
- **Authentication:** in-cluster only
- **Data owned:** users, profiles, ideas, versions, verdicts, scores, approvals, conversations
- **Observability:** cache hit/miss
- **Security:** password hashes only; no private source data
- **Deployment:** Deployment, PVC for Postgres
- **Requirements:** M02-*, DBS-001

## M3 Orchestrator
- **Units:** orchestrator
- **Inputs:** discover/validate requests, answers, approvals
- **Outputs:** run states, events, results
- **Depends on:** M2, M6, M7-M12, M13
- **API boundary:** internal run API
- **Error handling:** retries, timeouts, budget pause
- **Authentication:** in-cluster
- **Data owned:** run state
- **Observability:** every decision traced
- **Security:** enforces budgets and round limits
- **Deployment:** Deployment
- **Requirements:** M03-*, VAL-*, DSC-004

## M4 Scouts
- **Units:** scouts
- **Inputs:** source name, query
- **Outputs:** raw fetched items
- **Depends on:** M5, M6i
- **API boundary:** CronJob and on demand
- **Error handling:** per-source back-off; skip failed source
- **Authentication:** none (no keys held)
- **Data owned:** none
- **Observability:** items fetched, failures
- **Security:** internet only via M5
- **Deployment:** CronJob
- **Requirements:** M04-*

## M5 Tool layer
- **Units:** tools
- **Inputs:** fetch (and proposed llm) requests
- **Outputs:** sanitised content
- **Depends on:** internet
- **API boundary:** POST /fetch
- **Error handling:** refuse disallowed domain or robots path; 429 on limit
- **Authentication:** holds external keys (Secrets)
- **Data owned:** fetch cache
- **Observability:** allow/deny, blocked injections, cost
- **Security:** allow-list, sanitiser, only egress
- **Deployment:** Deployment, label app=tools
- **Requirements:** M05-*, API-007, ETH-*

## M6 Knowledge base
- **Units:** kb
- **Inputs:** queries with filters; cards to index
- **Outputs:** ranked evidence items with ids
- **Depends on:** vector store, Postgres
- **API boundary:** POST /search
- **Error handling:** empty result is explicit
- **Authentication:** in-cluster
- **Data owned:** cards, card_sources, chunks
- **Observability:** retrieval latency, freshness, coverage
- **Security:** returns data, never instructions
- **Deployment:** Deployment, vector PVC
- **Requirements:** M06-*, API-008

## M6i Ingestion
- **Units:** ingestion job
- **Inputs:** fetched items
- **Outputs:** idea cards, chunks, snapshot, run stats
- **Depends on:** M6, M5 cache
- **API boundary:** CronJob
- **Error handling:** idempotent rerun
- **Authentication:** in-cluster
- **Data owned:** ingestion_runs
- **Observability:** added, dropped
- **Security:** keeps only card fields
- **Deployment:** CronJob
- **Requirements:** M6I-*, ETH-006

## M7 Niche and trend analyst
- **Units:** analyst
- **Inputs:** cards
- **Outputs:** named niches, monthly series, gaps
- **Depends on:** M6
- **API boundary:** internal
- **Error handling:** too few cards → 'unknown'
- **Authentication:** in-cluster
- **Data owned:** niches, niche_stats
- **Observability:** cluster counts
- **Security:** none beyond data rules
- **Deployment:** Deployment
- **Requirements:** M07-*

## M8 Idea generator
- **Units:** ideation
- **Inputs:** profile, niches, gaps
- **Outputs:** ideas citing gap evidence
- **Depends on:** M6, M7, M12, hosted or local model
- **API boundary:** internal
- **Error handling:** max 3 rounds; drop defeated
- **Authentication:** in-cluster
- **Data owned:** debate record in trace
- **Observability:** rounds, drops, tokens
- **Security:** evidence required
- **Deployment:** Deployment
- **Requirements:** M08-*, DSC-*

## M9 Validators
- **Units:** validators
- **Inputs:** idea, profile, evidence, features
- **Outputs:** dimension scores or abstentions
- **Depends on:** M6, M7, M10
- **API boundary:** internal
- **Error handling:** invalid output → retry once → fallback
- **Authentication:** in-cluster
- **Data owned:** none
- **Observability:** per-scorer latency, abstentions
- **Security:** evidence ids must exist in KB
- **Deployment:** Deployment
- **Requirements:** M09-*, DIM-*

## M10 Scoring model
- **Units:** scorer
- **Inputs:** rubric, idea, evidence
- **Outputs:** dimension score JSON
- **Depends on:** model artefact; fallback via M5
- **API boundary:** POST /score
- **Error handling:** schema check, retry once, fallback, log
- **Authentication:** in-cluster
- **Data owned:** model files (volume)
- **Observability:** fallbacks, latency, cost
- **Security:** treats evidence as data
- **Deployment:** Deployment, measured limits
- **Requirements:** M10-*, FT-006..008

## M10t Fine-tuning
- **Units:** jobs/finetune (offline)
- **Inputs:** KB examples, rubrics, human checks
- **Outputs:** model artefact, metrics
- **Depends on:** free GPU, hosted model
- **API boundary:** documented commands
- **Error handling:** fail loudly on leakage
- **Authentication:** personal API keys outside repo
- **Data owned:** datasets
- **Observability:** loss, evaluation table
- **Security:** no labelled-verdict ideas
- **Deployment:** import Job
- **Requirements:** M10T-001, FT-*

## M11 Verdict engine
- **Units:** verdict
- **Inputs:** six scores, profile, config
- **Outputs:** verdict JSON
- **Depends on:** ConfigMap only
- **API boundary:** POST /verdict, /whatif
- **Error handling:** reject invalid input
- **Authentication:** in-cluster
- **Data owned:** none (pure)
- **Observability:** decision trace
- **Security:** no network, no model
- **Deployment:** Deployment
- **Requirements:** M11-*, GAT-*, SCR-*, FLW-001

## M12 Critic and guardrails
- **Units:** critic
- **Inputs:** claims with evidence ids; user and fetched text
- **Outputs:** supported or not per claim; blocks
- **Depends on:** M6
- **API boundary:** POST /check
- **Error handling:** unsupported → removed
- **Authentication:** in-cluster
- **Data owned:** approvals decisions via M2
- **Observability:** blocked injections
- **Security:** input rail, injection defence
- **Deployment:** Deployment
- **Requirements:** M12-*, API-011

## M13 AgenticOps
- **Units:** agentops
- **Inputs:** trace records
- **Outputs:** traces, metrics, replay, drift, dashboard
- **Depends on:** trace volume, M2
- **API boundary:** POST /trace, GET /runs/{id}/trace
- **Error handling:** never blocks a run
- **Authentication:** in-cluster
- **Data owned:** traces/*.jsonl, traces_index
- **Observability:** all metrics
- **Security:** no secrets in traces
- **Deployment:** Deployment, eval Job
- **Requirements:** M13-*, OPS-*

## M14 Platform
- **Units:** .github, Jenkinsfile, k8s, scripts
- **Inputs:** commits
- **Outputs:** checks, images, deployments
- **Depends on:** GitHub, registry, cluster
- **API boundary:** pipelines
- **Error handling:** stop and roll back
- **Authentication:** Jenkins credentials store
- **Data owned:** none
- **Observability:** pipeline results
- **Security:** protected branches, scans
- **Deployment:** n/a
- **Requirements:** M14-*, CIC-*, JNK-*, K8S-*, NET-*
