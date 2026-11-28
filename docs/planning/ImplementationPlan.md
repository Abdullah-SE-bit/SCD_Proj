# Implementation plan

Generated from `harness/task-registry/tasks.json`. Phases after 0 are proposed and blocked until their gate dependencies are done and the decisions in `docs/requirements/PendingDecisions.md` that affect them are made.

## P00: Foundation and development harness

Demonstrable result: Protected branches, green Phase 0 checks, reviewed promotion PR.

### P00.01 Ingest documents and build requirements registry

Audit both PDFs; extract traceable requirements and ambiguities.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status done
- Depends on: nothing
- Requirements: DDR-001, IFC-001
- File scope: `docs/**`, `harness/**`
- Deliverables: Registry, audit, ambiguity list
- Acceptance: Every mandatory statement recorded with page and section
- Tests: requirements-registry check
- Verify: `python harness/verification/scd.py all`
- Evidence: DocumentIngestionAudit.md
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P00.02 Protect branches and set up GitHub workflow

Protect main and dev, PR and issue templates, merge policy.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status done
- Depends on: nothing
- Requirements: M14-001, GIT-001, GIT-002, CIC-006
- File scope: `.github/**`, `docs/**`
- Deliverables: Protection settings and templates
- Acceptance: Protection verified by API; direct push rejected
- Tests: branch probes
- Verify: `python harness/verification/scd.py repo-structure`
- Evidence: docs/evidence/phase0/
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P00.03 Architecture, contracts and plan

MVP, architecture, schemas, OpenAPI, task plan.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status done
- Depends on: P00.01
- Requirements: IFC-002, API-001, SCH-001, SCH-002, SCH-003, SCH-004, SCH-005, SCH-006
- File scope: `docs/**`, `contracts/**`, `config/**`, `rubrics/**`, `eval/**`
- Deliverables: Specifications and contracts
- Acceptance: Contracts validate against guide examples
- Tests: contract-tests
- Verify: `python harness/verification/scd.py check contract-tests`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P00.04 Development harness

Skills, subagents, rules, hooks, verification scripts and tests.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status done
- Depends on: P00.01
- Requirements: DOC-001, SEC-002, LOG-001
- File scope: `.claude/**`, `harness/**`, `CLAUDE.md`, `AGENTS.md`
- Deliverables: Harness with negative tests
- Acceptance: Negative tests detect each forbidden action
- Tests: harness-tests
- Verify: `python -m unittest discover -s harness/tests`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P00.05 CI, Jenkins, Docker and Kubernetes foundation

Required check workflow, Jenkinsfile, manifests scaffold.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status done
- Depends on: P00.04
- Requirements: M14-002, CIC-005, SET-003, REP-001, NET-001
- File scope: `.github/**`, `k8s/**`, `Jenkinsfile`, `docker-compose.yml`, `.env.example`, `scripts/**`
- Deliverables: CI workflow and scaffolds
- Acceptance: All Phase 0 checks green on the PR
- Tests: ci-gate
- Verify: `python harness/verification/scd.py all`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P00.06 Independent review of foundation

Secondary contributor audits PDFs against registry, reviews harness and approves promotion.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status done
- Depends on: P00.02, P00.03, P00.05
- Requirements: COL-002
- File scope: `docs/handoff/**`, `docs/evidence/**`
- Deliverables: Review report
- Acceptance: Human collaborator approval on promotion PR
- Tests: review checklist
- Verify: `python harness/verification/scd.py all`
- Evidence: PR review
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P00 Phase 0 gate

All Phase 0 tasks verified and merged into main.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity S; status done
- Depends on: P00.01, P00.02, P00.03, P00.04, P00.05, P00.06
- Requirements: GIT-001
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Protected branches, green Phase 0 checks, reviewed promotion PR.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: merge commit
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P01: Walking skeleton on Kubernetes (fixtures only)

Demonstrable result: Browser submits an idea and sees a fixture verdict card served end to end from the cluster.

### P01.01 Cluster with enforced NetworkPolicy

kind plus Calico, namespace, default-deny and M5 egress.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status done
- Depends on: P00
- Requirements: SET-001, NET-001, NET-002, K8S-001, K8S-010
- File scope: `k8s/**`, `scripts/**`, `docs/**`
- Deliverables: Cluster script and policies
- Acceptance: Egress blocked for non-M5, allowed for M5
- Tests: egress test
- Verify: `scripts/netpol_test.sh`
- Evidence: test output
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P01.02 Service skeleton and images

One minimal service per module with /health and /ready, multi-stage non-root Dockerfile, pinned deps.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status done
- Depends on: P00
- Requirements: API-002, REP-002, M14-004, DKR-001, DKR-002, GEN-006
- File scope: `services/**`, `jobs/**`, `tests/**`, `requirements*.txt`, `.dockerignore`
- Deliverables: Images for every module
- Acceptance: Every image builds, runs non-root, answers probes
- Tests: probe tests
- Verify: `python harness/verification/scd.py check backend-unit-tests`; `python harness/verification/scd.py check docker-build`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P01.03 Thin UI and gateway path

UI to gateway to orchestrator to fixture verdict, API address at runtime.

- Module M1; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status done
- Depends on: P00
- Requirements: ARC-001, M01-002, CMN-005, CMN-008
- File scope: `services/ui/**`, `services/gateway/**`, `tests/**`
- Deliverables: Walking UI
- Acceptance: Card clearly labelled FIXTURE DATA
- Tests: component tests
- Verify: `npm --prefix services/ui test`
- Evidence: screenshot
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P01.04 Deploy skeleton to cluster

Deployments, Services, Ingress, probes, rolling update, compose for dev.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status done
- Depends on: P01.01, P01.02, P01.03
- Requirements: K8S-002, K8S-007, K8S-008, SET-002, SET-004
- File scope: `k8s/**`, `docker-compose.yml`, `README.md`, `scripts/**`
- Deliverables: Running skeleton
- Acceptance: All pods ready; README steps work
- Tests: smoke test
- Verify: `scripts/smoke_test.sh`
- Evidence: kubectl get pods
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P01.05 Jenkins delivery of skeleton

Jenkins in container, SCM polling, build, push, deploy, smoke, rollback.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status done
- Depends on: P01.04
- Requirements: M14-003, JNK-001, JNK-002, JNK-003, JNK-004, DKR-003, CIC-001
- File scope: `Jenkinsfile`, `scripts/**`, `docs/**`
- Deliverables: Working pipeline
- Acceptance: Green and deliberately failing run; rollback shown
- Tests: pipeline run
- Verify: `scripts/smoke_test.sh`
- Evidence: Jenkins screenshots
- Needs: human, credentials
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P01 Phase 1 gate

All Phase 1 tasks merged and demonstrated.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity S; status done
- Depends on: P00, P01.01, P01.02, P01.03, P01.04, P01.05
- Requirements: CMN-008
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Browser submits an idea and sees a fixture verdict card served end to end from the cluster.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P02: Accounts, profile, history and cache

Demonstrable result: Register, log in, edit profile, see idea history.

### P02.01 Migrations and repositories

Postgres schema and layered M2 backend.

- Module M2; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P01
- Requirements: M02-001, M02-002, M02-005, DBS-001
- File scope: `services/profile/**`, `contracts/database/**`, `tests/**`
- Deliverables: Migrations and repositories
- Acceptance: Fresh DB migrates; repositories tested
- Tests: integration
- Verify: `python harness/verification/scd.py check backend-unit-tests`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P02.02 Authentication, rate limits and validation

Register, login, profile endpoints at the gateway.

- Module M1; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P02.01
- Requirements: M01-003, API-003, SCH-002, SEC-001
- File scope: `services/gateway/**`, `services/profile/**`, `tests/**`
- Deliverables: Auth and profile
- Acceptance: Invalid, unauthenticated, over-limit rejected
- Tests: security tests
- Verify: `python harness/verification/scd.py check backend-unit-tests`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P02.03 History, versions, comparison and cache

Idea versions, compare, Redis cache keyed by profile, rubric, engine and snapshot versions.

- Module M2; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P02.01
- Requirements: USR-009, M02-003, M02-004, CMN-002, API-006, DBS-003
- File scope: `services/profile/**`, `services/gateway/**`, `tests/**`
- Deliverables: History and cache
- Acceptance: Version change misses cache; hit visible
- Tests: unit
- Verify: `python harness/verification/scd.py check backend-unit-tests`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P02.04 Profile and history screens

Profile editor, history, comparison with component tests.

- Module M1; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P02.02, P02.03
- Requirements: M01-001, M01-004
- File scope: `services/ui/**`, `tests/**`
- Deliverables: Screens
- Acceptance: Component tests cover states
- Tests: component
- Verify: `npm --prefix services/ui test`
- Evidence: screenshots
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P02 Phase 2 gate

All Phase 2 tasks merged and demonstrated.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity S; status not done
- Depends on: P01, P02.01, P02.02, P02.03, P02.04
- Requirements: IFC-002
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Register, log in, edit profile, see idea history.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P03: Deterministic Verdict Engine

Demonstrable result: POST scores to the engine and get gates, verdict, stability and what-if.

### P03.01 Gates, score, thresholds and confidence

Pure functions with config from ConfigMap.

- Module M11; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status done
- Depends on: P01
- Requirements: M11-001, M11-002, M11-003, GAT-001, GAT-002, GAT-003, GAT-004, GAT-005, FLW-001, SCR-001, SCR-002, SCR-003, SCR-004, SCR-005, SCR-006, SCH-005, API-010, VER-001, CMN-003
- File scope: `services/verdict/**`, `config/**`, `tests/**`, `k8s/**`
- Deliverables: Engine core
- Acceptance: Every gate and threshold edge tested; worked example 70.5
- Tests: verdict unit tests
- Verify: `pytest services/verdict -q`
- Evidence: CI run
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P03.02 Challenge, sensitivity and what-if

Adjustments, 14-run sensitivity, smallest change search.

- Module M11; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status not done
- Depends on: P03.01
- Requirements: M11-004, SCR-007, SCR-008, SCR-009, SCR-010, SCR-011, USR-011
- File scope: `services/verdict/**`, `tests/**`
- Deliverables: Stability features
- Acceptance: Worked example numbers reproduced
- Tests: verdict unit tests
- Verify: `pytest services/verdict -q`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P03.03 Rubrics for six dimensions

Versioned rubric files with anchors and worked examples; students review content.

- Module M9; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P01
- Requirements: RUB-001, DIM-001, DIM-002, VER-002
- File scope: `rubrics/**`, `contracts/schemas/**`
- Deliverables: Six rubrics
- Acceptance: Each anchor 0-5 has an example; both students reviewed
- Tests: contract
- Verify: `python harness/verification/scd.py check contract-tests`
- Evidence: review record
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P03 Phase 3 gate

All Phase 3 tasks merged and demonstrated.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity S; status not done
- Depends on: P01, P03.01, P03.02, P03.03
- Requirements: CIC-002
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: POST scores to the engine and get gates, verdict, stability and what-if.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P04: Data collection and knowledge base

Demonstrable result: Search 1,500+ real cards with citations and measured retrieval quality.

### P04.01 Tool layer

Allow-list, robots.txt, rate limit, cache, sanitiser, egress.

- Module M5; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status done
- Depends on: P01
- Requirements: M05-001, M05-002, M05-003, API-007, DAT-001, ETH-001, ETH-002, ARC-007, NET-003
- File scope: `services/tools/**`, `k8s/**`, `tests/**`, `config/**`
- Deliverables: M5
- Acceptance: Poisoned page neutralised; egress test recorded
- Tests: security
- Verify: `pytest services/tools -q`; `scripts/netpol_test.sh`
- Evidence: evidence
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P04.02 Scouts for three sources

Connectors, CronJob and on-demand, failure handling.

- Module M4; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P04.01
- Requirements: M04-001, M04-002, M04-003, K8S-003
- File scope: `services/scouts/**`, `jobs/ingestion/**`, `k8s/**`, `tests/**`
- Deliverables: Scouts
- Acceptance: Three sources fetched via M5 only
- Tests: integration
- Verify: `pytest services/scouts -q`
- Evidence: logs
- Needs: credentials
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P04.03 Ingestion pipeline and 1,500 cards

Dedupe, chunk, embed, index, snapshot.

- Module M6i; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P04.02
- Requirements: M6I-001, M6I-002, M6I-003, ETH-003, ETH-006, SCH-001, DBS-002
- File scope: `jobs/ingestion/**`, `services/kb/**`, `tests/**`, `docs/**`
- Deliverables: Cards and snapshot
- Acceptance: >=1500 cards, re-run adds none
- Tests: integration
- Verify: `pytest jobs/ingestion -q`
- Evidence: counts report
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P04.04 Hybrid retrieval and reranking

Search API with filters, citations, freshness.

- Module M6; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P04.03
- Requirements: M06-001, M06-002, M06-003, M06-004, M06-005, API-008, SCH-003, ARC-003, ETH-004
- File scope: `services/kb/**`, `tests/**`
- Deliverables: M6 search
- Acceptance: Filters and ids tested
- Tests: integration
- Verify: `pytest services/kb -q`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P04.05 Retrieval evaluation and CI gate

Students hand-write 20+ queries with relevant cards; baseline stored.

- Module M6; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P04.04
- Requirements: M06-006, CIC-003, CMN-006
- File scope: `eval/retrieval/**`, `harness/**`, `.github/**`
- Deliverables: Queries, baseline, gate
- Acceptance: Seeded regression fails
- Tests: eval
- Verify: `pytest eval/retrieval -q`
- Evidence: results json
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P04 Phase 4 gate

All Phase 4 tasks merged and demonstrated.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity S; status not done
- Depends on: P03, P04.01, P04.02, P04.03, P04.04, P04.05
- Requirements: M6I-003
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Search 1,500+ real cards with citations and measured retrieval quality.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P05: Validate workflow with scorers and guardrails

Demonstrable result: Validate a real idea with live progress and evidence-linked card. Traces, replay and budget stops are visible.

### P05.01 Feature computation and four scorers

Parallel scorers, schemas, abstention; hosted model behind interface.

- Module M9; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P04
- Requirements: M09-001, M09-002, M09-003, M09-004, VAL-003, VAL-004, DIM-003, SCH-004, API-009
- File scope: `services/validators/**`, `services/scorer/**`, `rubrics/**`, `tests/**`
- Deliverables: Scorers
- Acceptance: Evidence-free score abstains
- Tests: unit
- Verify: `pytest services/validators -q`
- Evidence: CI run
- Needs: credentials
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P05.02 Validate state machine

Intake, clarify, evidence, scorers, verdict, challenge, stability, card; retries, budgets, approval.

- Module M3; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status not done
- Depends on: P04, P05.05, P05.06
- Requirements: M03-001, M03-002, M03-003, M03-004, M03-005, VAL-001, VAL-002, VAL-005, VAL-006, USR-004, USR-005, ARC-002, ARC-004, CMN-001
- File scope: `services/orchestrator/**`, `tests/**`
- Deliverables: Orchestrator
- Acceptance: State transitions and budget pause tested
- Tests: unit
- Verify: `pytest services/orchestrator -q`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P05.03 Critic and guardrails

Claim check, injection defence, input rail, challenge handling.

- Module M12; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P04
- Requirements: M12-001, M12-002, M12-003, M12-004, API-011, USR-008, ETH-005, CMN-004
- File scope: `services/critic/**`, `tests/**`
- Deliverables: M12
- Acceptance: Unsupported claims removed
- Tests: security
- Verify: `pytest services/critic -q`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P05.04 Run APIs, live progress and verdict card

SSE stream, approvals, card, insufficient evidence view.

- Module M1; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P05.02, P05.01, P05.03
- Requirements: USR-003, USR-006, USR-010, GEN-003, API-004, API-005, USR-007
- File scope: `services/gateway/**`, `services/ui/**`, `tests/**`
- Deliverables: Interactive Validate
- Acceptance: All card elements and live spend shown
- Tests: component and e2e
- Verify: `npm --prefix services/ui test`
- Evidence: screenshots
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P05.05 Tracing and replay

Trace APIs, JSON lines, replay.

- Module M13; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P04
- Requirements: M13-001, OPS-001, OPS-002, API-012, SCH-006, ARC-006, K8S-009
- File scope: `services/agentops/**`, `services/**`, `tests/**`
- Deliverables: Tracing
- Acceptance: Replay reproduces decisions
- Tests: behaviour
- Verify: `pytest services/agentops -q`
- Evidence: trace
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P05.06 Budgets and registry

Caps for tokens, pages, steps, cost; prompt and rubric registry.

- Module M13; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P05.05
- Requirements: M13-002, M13-003, OPS-003, OPS-004
- File scope: `services/agentops/**`, `services/orchestrator/**`, `services/tools/**`, `config/**`, `tests/**`
- Deliverables: Budgets
- Acceptance: Each cap tested
- Tests: unit
- Verify: `pytest services/agentops -q`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P05 Phase 5 gate

All Phase 5 tasks merged and demonstrated.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity S; status not done
- Depends on: P04, P05.01, P05.02, P05.03, P05.04, P05.05, P05.06
- Requirements: VAL-006
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Validate a real idea with live progress and evidence-linked card.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P06: Fine-tuned scoring model

Demonstrable result: Comparison table of base, tuned and hosted models; scoring served locally.

### P06.01 Build and hand-check dataset

300+ train examples plus 60+ hand-checked evaluation examples, split by idea.

- Module M10t; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P04, P03
- Requirements: FT-001, FT-002, FT-003, FT-004, M10-002, M10-003
- File scope: `jobs/finetune/**`, `eval/scoring/**`, `tests/**`
- Deliverables: Dataset with annotator marks
- Acceptance: No idea in both splits; students checked labels
- Tests: leakage test
- Verify: `pytest jobs/finetune -q`
- Evidence: coverage matrix
- Needs: human, credentials
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P06.02 Train, merge and quantise

QLoRA on free GPU; record settings and loss.

- Module M10t; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P06.01
- Requirements: M10-001, FT-005, FT-006, FT-011, M10T-001, ARC-005
- File scope: `jobs/finetune/**`, `docs/**`
- Deliverables: Model artefact
- Acceptance: Reproducible documented commands
- Tests: script checks
- Verify: `pytest jobs/finetune -q`
- Evidence: loss curve
- Needs: human, gpu
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P06.03 Serve model with fallback

Own container, schema validation, retry once, hosted fallback.

- Module M10; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P06.02
- Requirements: FT-007, FT-008, M10-004
- File scope: `services/scorer/**`, `k8s/**`, `tests/**`
- Deliverables: Model server
- Acceptance: Fallback logged
- Tests: behaviour
- Verify: `pytest services/scorer -q`
- Evidence: kubectl top
- Needs: credentials
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P06.04 Model comparison

Base, tuned, hosted on hand-checked set with all metrics and a failure case.

- Module M10t; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P06.03
- Requirements: FT-009, FT-010, M10-005
- File scope: `jobs/evaluation/**`, `eval/scoring/**`, `docs/**`
- Deliverables: Comparison table
- Acceptance: All metrics measured
- Tests: eval
- Verify: `pytest jobs/evaluation -q`
- Evidence: results json
- Needs: credentials
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P06 Phase 6 gate

All Phase 6 tasks merged and demonstrated.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity S; status not done
- Depends on: P05, P06.01, P06.02, P06.03, P06.04
- Requirements: K8S-005
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Comparison table of base, tuned and hosted models; scoring served locally.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P07: Niche analysis and Discover workflow

Demonstrable result: Discover returns ranked gap-based ideas with cards.

### P07.01 Niche and trend analyst

Clustering, naming, monthly series, rising/flat/saturated, gaps.

- Module M7; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P04
- Requirements: M07-001, M07-002, GEN-001
- File scope: `services/analyst/**`, `tests/**`
- Deliverables: M7
- Acceptance: Series and gaps produced
- Tests: unit
- Verify: `pytest services/analyst -q`
- Evidence: niche map
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P07.02 Idea generator debate

Ideator, Gap Analyst, Skeptic, 3 rounds max.

- Module M8; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status not done
- Depends on: P07.01, P05
- Requirements: M08-001, M08-002, DSC-001, DSC-002, DSC-003, CMN-007
- File scope: `services/ideation/**`, `tests/**`
- Deliverables: M8
- Acceptance: Round cap and citations tested
- Tests: behaviour
- Verify: `pytest services/ideation -q`
- Evidence: trace
- Needs: credentials
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P07.03 Discover workflow and results screen

Survivors validated and ranked.

- Module M3; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P07.02
- Requirements: DSC-004, USR-002, GEN-002, USR-001
- File scope: `services/orchestrator/**`, `services/ui/**`, `tests/**`
- Deliverables: Discover
- Acceptance: Ranked cards with reasons
- Tests: e2e
- Verify: `pytest services/orchestrator -q`
- Evidence: screenshot
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P07 Phase 7 gate

All Phase 7 tasks merged and demonstrated.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity S; status not done
- Depends on: P06, P07.01, P07.02, P07.03
- Requirements: USR-011
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Discover returns ranked gap-based ideas with cards.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P08: AgenticOps evaluation, drift and dashboard

Demonstrable result: Behaviour tests pass; evaluation Job, dashboard and drift report shown.

### P08.01 Behaviour tests

Recorded responses: invalid JSON, timeout, empty source, poisoned page.

- Module M13; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P05
- Requirements: OPS-009
- File scope: `eval/agent-behaviour/**`, `tests/**`
- Deliverables: Replay tests
- Acceptance: Four cases pass without live model
- Tests: behaviour
- Verify: `pytest eval/agent-behaviour -q`
- Evidence: CI run
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P08.02 Evaluation harness, drift and dashboard

Harness as Job, drift reports, dashboard metrics.

- Module M13; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P05.05, P09.01
- Requirements: M13-004, M13-005, M13-006, OPS-005, OPS-006, OPS-007, OPS-008
- File scope: `jobs/evaluation/**`, `services/agentops/**`, `services/ui/**`, `k8s/**`, `Jenkinsfile`
- Deliverables: Harness and dashboard
- Acceptance: Job and nightly run shown
- Tests: eval
- Verify: `pytest jobs/evaluation -q`
- Evidence: screenshots
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P08 Phase 8 gate

All Phase 8 tasks merged and demonstrated.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity S; status not done
- Depends on: P07, P08.01, P08.02
- Requirements: OPS-009
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Replay a run, view dashboard and drift report.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P09: Verdict tuning on human labels

Demonstrable result: Before and after confusion matrices.

### P09.01 Human labelled verdict set

Both students label independently, resolve differences, record annotators.

- Module M11; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity L; status not done
- Depends on: P03
- Requirements: TUN-001, TUN-002
- File scope: `eval/verdict/**`, `docs/**`
- Deliverables: Labelled set
- Acceptance: Both annotators recorded; no AI-authored labels
- Tests: schema
- Verify: `python harness/verification/scd.py check contract-tests`
- Evidence: annotation log
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P09.02 Baseline, tuning and final matrices

Confusion matrix before and after; separate false-GO error.

- Module M11; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity M; status not done
- Depends on: P08, P09.01
- Requirements: TUN-003, TUN-004, TUN-005
- File scope: `eval/verdict/**`, `config/**`, `k8s/**`, `docs/**`
- Deliverables: Matrices
- Acceptance: Measured from real runs
- Tests: eval
- Verify: `pytest jobs/evaluation -q`
- Evidence: matrices
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P09 Phase 9 gate

All Phase 9 tasks merged and demonstrated.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity S; status not done
- Depends on: P08, P09.01, P09.02
- Requirements: OPS-005
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Gate record
- Acceptance: Before and after confusion matrices.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: demo log
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

## P10: Hardening, demonstrations and submission

Demonstrable result: Rollout, rollback, NetworkPolicy test, report and screenshots.

### P10.01 Resource measurement, autoscaling and platform demos

kubectl top measurements, HPA, rollout, rollback, pods.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity M; status not done
- Depends on: P09
- Requirements: K8S-004, K8S-006, M14-005, M11-003, SUB-006
- File scope: `k8s/**`, `docs/**`, `scripts/**`
- Deliverables: Measured limits
- Acceptance: Limits traceable to measurements
- Tests: load test
- Verify: `scripts/smoke_test.sh`
- Evidence: screenshots
- Needs: nothing special
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P10.02 Merge-conflict exercise

Two branches edit the same lines; resolve in a PR.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity S; status not done
- Depends on: P09
- Requirements: GIT-004, GIT-003, SUB-005
- File scope: `docs/**`
- Deliverables: Conflict PR
- Acceptance: PR and screenshot
- Tests: manual
- Verify: `python harness/verification/scd.py all`
- Evidence: screenshot
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P10.03 Report, screenshots and decision records

10-page report, evidence register, 3+ DDRs, security pass.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity L; status not done
- Depends on: P10.01, P10.02
- Requirements: SUB-001, SUB-002, SUB-003, SUB-004, SUB-007, SUB-008, SUB-009, DDR-001, CIC-004, SEC-002, SET-003
- File scope: `docs/**`, `README.md`
- Deliverables: Submission package
- Acceptance: Every checklist row has evidence
- Tests: release check
- Verify: `python harness/verification/scd.py all`
- Evidence: report PDF
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P10.04 Contribution table, access check and viva

Truthful table, signatures, both can explain system.

- Module M14; owner `Abdullah-SE-bit`; reviewer `Demidoga`; complexity S; status not done
- Depends on: P10.03
- Requirements: SUB-010, LOG-002, COL-001, COL-002, COL-003, SUB-002
- File scope: `docs/**`
- Deliverables: Signed table
- Acceptance: Signed by both students
- Tests: manual
- Verify: `python harness/verification/scd.py all`
- Evidence: signed PDF
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.

### P10 Phase 10 gate

Submission verified.

- Module M14; owner `Demidoga`; reviewer `Abdullah-SE-bit`; complexity S; status not done
- Depends on: P09, P10.01, P10.02, P10.03, P10.04
- Requirements: SUB-001, GEN-004, GEN-005
- File scope: `docs/**`, `harness/task-registry/status/**`
- Deliverables: Release record
- Acceptance: Rollout, rollback, NetworkPolicy test, report and screenshots.
- Tests: all checks
- Verify: `python harness/verification/scd.py all`
- Evidence: submission receipt
- Needs: human
- Done when: Acceptance criteria met, listed tests pass in CI, docs, handoff and AI-usage log updated, evidence stored, PR into dev merged and status file present.
