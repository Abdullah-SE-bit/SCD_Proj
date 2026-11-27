# Document ingestion audit

Performed 2026-11-28 by Claude Code (primary session). Awaiting independent audit (task P00.06).

| Document | Pages | Size | SHA-256 |
|---|---|---|---|
| Semester_Project_Description.pdf | 6 (verified) | 496.1 KB | `2cce1937b4613e27e33eb1a1ca071334a48dd2395b882248f822a31a544d53ba` |
| Semester_Project_Guide.pdf | 8 (verified) | 278.7 KB | `2c4fc015ef7ef44716886e253f73a63eb673b65bd83345aa3d13e01a4f16ffc7` |

## Method
1. Every page viewed as a rendered image (14 of 14).
2. Text extracted with `pdftotext -layout` and read in full (26,270 and 30,450 bytes) and compared with the pages.
3. Diagrams re-rendered at higher resolution: the architecture raster (2400x1600) extracted with `pdfimages`,
   and crops of the decision flow and data model at 220 dpi. Other diagrams were read from the page renders.

Layout extraction scrambles tables and code blocks (for example the U1-U10 table, the contents lists and the
Guide 4.4 Dockerfile), so the page images were treated as authoritative wherever the two differed.

## Section coverage

| Document | Page | Sections | Requirement prefixes |
|---|---|---|---|
| Description | 1 | 1 Overview, 1.1-1.3 | GEN, COL, DOC, DAT, SEC |
| Description | 2 | 2 User table, 3 Architecture | USR, ARC |
| Description | 3 | 3.1, 3.2, 4 Modules (M1-M6) | DSC, VAL, M01-M06 |
| Description | 4 | 4 Modules (M6i-M14), 5, 5.1 | M6I-M14, VER, DIM |
| Description | 5 | 5.2, 5.3 | GAT, FLW, SCR |
| Description | 6 | 5.4, 6 Submission | SCR-011, SUB |
| Guide | 1 | 1, 2 | IFC, DBS |
| Guide | 2 | 2.1-2.3, 3 | SCH, API |
| Guide | 3 | 3, 4.1-4.4 | API, REP, GIT, SET, DKR |
| Guide | 4 | 5, 6.1-6.3, 7 | ETH, FT, OPS |
| Guide | 5 | 7, 8, 8.1, 8.2 | OPS, CIC, JNK |
| Guide | 6 | 8.2, 9, 9.1, 9.2 | JNK, K8S |
| Guide | 7 | 9.2, 9.3, 10 | NET, TUN, RUB |
| Guide | 8 | 11, 12 | DDR, LOG, CMN |

## Diagrams (7 of 7)

| Diagram | Captured relationships |
|---|---|
| D Fig.1 Architecture (p2) | User↔M1 (chat/progress stream); M1↔M3; M3↔M2; M3↔M12; M3→M8, M7, M9; M8, M7, M9↔M6; M9→M10 "scores"; M10→M11; M11→M12 "verdict"; M10t→M10 "model" (M10t dashed, offline); external sources↔M5↔M4→M6i→M6; dotted telemetry to M13; GitHub→Actions→Jenkins→Registry→deploy to cluster |
| D Fig.2 Discover (p3) | 8 steps with module labels; loop of steps 3-6 up to 3 rounds |
| D Fig.3 Validate (p3) | 8 steps with module labels; "only the Verdict Engine decides" |
| D Fig.4 Decision flow (p5) | 4 gates, weighted score, confidence check, GO/floor check, T_no split, sensitivity holds/flips |
| G Fig.1 Records (p1) | Postgres entities and arrows users→profiles→ideas→idea_versions→verdicts→dimension_scores; approvals, traces_index, conversations; cards→card_sources, cards→vector store; niches, niche_stats, ingestion_runs; files on volumes; Redis with TTL |
| G Fig.2 CI/CD (p5) | PR→Actions (7 checks)→merge needs all green→Jenkins (6 stages); fail stops; rollback |
| G Fig.3 Cluster (p6) | Namespace idea-validator: Ingress, Deployments, StatefulSets/PVCs, CronJobs, Jobs, ConfigMaps, Secrets, NetworkPolicy, per-workload rules, observability, rollout |

## Tables, formulas, schemas, examples
All captured: project-at-a-glance, U1-U10, modules, dimensions, gates, weight presets, public and internal
endpoints, AgenticOps capabilities, Kubernetes objects, decision-record, AI-log and contribution templates.
Formulas: weighted score, confidence, challenge adjustment, sensitivity. Numbers: the 5.4 worked example
(recomputed: 70.5, 69.867, 73.5, 73.067). Schemas: card, profile, evidence, dimension score, verdict, trace,
training line, rubric file. Code examples: Dockerfile, Actions workflow, Jenkinsfile, Deployment/CronJob, kubectl.

## Results
- Requirements extracted: see [Requirements](Requirements.md) (237; 234 mandatory, 3 recommended).
- Ambiguities and contradictions: [Ambiguities](Ambiguities.md).
- Unreadable or inaccessible content: none found.
- Referenced but not supplied: "Assignment 1" (Description p3, M2 layering). **Not ingested.**
- Not in either document: deadline, marking scheme, student roll numbers.
- A statement-level miss is still possible; the independent audit in P00.06 exists to find it.
