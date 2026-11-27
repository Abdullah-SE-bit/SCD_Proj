# Architecture

Status: proposed, derived from Description Figure 1. Deviations are listed at the end.

## High level
```mermaid
flowchart TB
  U[Student browser] <-->|chat, progress stream| M1[M1 UI + API gateway]
  M1 <--> M3[M3 Orchestrator]
  M3 <--> M2[(M2 Profile, session, cache)]
  M3 <--> M12[M12 Critic and guardrails]
  M3 --> M8[M8 Idea generator]
  M3 --> M7[M7 Niche and trend]
  M3 --> M9[M9 Validators]
  M8 <--> M6[(M6 Knowledge base)]
  M7 <--> M6
  M9 <--> M6
  M9 -->|score request| M10[M10 Scoring model]
  M10t[M10t Fine-tuning, offline] -.model.-> M10
  M3 -->|six scores| M11[M11 Verdict engine]
  M11 -->|verdict| M3
  EXT[Public sources and hosted model] <--> M5[M5 Tool layer]
  M5 <--> M4[M4 Scouts]
  M4 --> M6i[M6i Ingestion] --> M6
  M3 -.telemetry.-> M13[M13 AgenticOps]
```
Every module sends telemetry to M13 (only one edge drawn).

## Containers
```mermaid
flowchart LR
  subgraph ns[namespace idea-validator]
    ing[Ingress] --> ui[ui] & gw[gateway]
    gw --> orch[orchestrator] & prof[profile]
    prof --> pg[(postgres PVC)] & rd[(redis)]
    orch --> val[validators] & ide[ideation] & an[analyst] & crit[critic] & ver[verdict]
    val --> sc[scorer]
    val & ide & an --> kb[kb]
    kb --> vec[(vector store PVC)] & pg
    scouts[[scouts CronJob]] --> tools[tools]
    scouts --> ingest[[ingestion CronJob]] --> kb
    ops[agentops] --> tv[(trace volume)]
    ev[[evaluation Job]] --> gw
  end
  tools --> net((internet))
```

## Service communication
JSON over HTTP inside the cluster, validated against `contracts/schemas` on both sides; Server-Sent Events from
gateway to browser (decision proposed: SSE is one-way, which is all progress needs; answers and approvals are
POSTs). The browser calls only the gateway. Services call each other by Kubernetes DNS name from configuration.

## Cross-cutting
- Correlation: every call carries `run_id`; each step writes a trace record.
- Errors: typed JSON error, bounded retries with timeouts in M3; a failed scorer abstains, it never invents.
- Auth: M1 issues and checks user tokens; internal services trust only in-cluster traffic restricted by
  NetworkPolicy.
- Data ownership: [DataArchitecture](DataArchitecture.md).

## Deviations from Figure 1 (to be stated in the report)
1. M3 calls M11 and passes its result to M12; the figure draws M10→M11→M12 (AMB-21).
2. Hosted model calls leave through M5 (AMB-04, pending D-06).
