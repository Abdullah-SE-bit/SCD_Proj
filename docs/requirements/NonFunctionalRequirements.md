# Non-functional, architecture, platform, security and process requirements

Generated from `docs/requirements/requirements.json`. Do not edit by hand. 107 requirements.

## M1

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| ARC-001 | Desc p2 §3 Fig.1 | mandatory | M1 is the browser's entry; chat and progress stream between user and M1; M1 talks to M3. | Browser only calls M1. | test | in_progress |
| M01-001 | Desc p3 §4 | mandatory | M1 Web UI and API Gateway is the only entrance: chat, live progress, verdict card, approval prompt, history. | All listed views exist behind M1. | e2e | unimplemented |
| M01-002 | Desc p3 §4 | mandatory | UI API address is set at runtime. | Same image runs against two API addresses. | test | implemented |
| M01-003 | Desc p3 §4 | mandatory | M1 has login, rate limits and input validation. | Unauthenticated, over-limit and invalid requests rejected. | test | unimplemented |
| SUB-007 | Desc p6 §6.3 | mandatory | Interface screenshots: profile, Discover results, verdict card, challenge, what-if version 2, INSUFFICIENT EVIDENCE. | Captured and captioned. | evidence | unimplemented |
| K8S-010 | Guide p6 §9 Fig.3 | mandatory | UI reaches the API only. | NetworkPolicy blocks UI to other services. | infra-test | implemented |
| CMN-005 | Guide p8 §12 | mandatory | Never call model or scouts from the browser; no hard-coded localhost in images. | Static check and NetworkPolicy. | ci | implemented |

## M2

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M02-004 | Desc p3 §4 | mandatory | Cache hits are visible. | Hits shown in trace and metrics. | test | unimplemented |
| M02-005 | Desc p3 §4 | mandatory | Layered backend (routes, services, repositories) as in Assignment 1. | Layering enforced by structure and review. | inspection | in_progress |

## M3

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| ARC-002 | Desc p2 §3 Fig.1 | mandatory | M3 supervises M8, M7 and M9 and exchanges data with M2 and M12. | Call graph matches diagram or deviation is documented. | inspection | unimplemented |
| M03-002 | Desc p3 §4 | mandatory | Parallel agents with retries and timeouts. | Retry and timeout tests pass. | test | unimplemented |
| M03-004 | Desc p3 §4 | mandatory | Re-run only what changed. | A what-if re-run skips unaffected steps. | test | unimplemented |
| M03-005 | Desc p3 §4 | mandatory | Every decision is traced. | Decision records present in trace. | test | unimplemented |
| CMN-001 | Guide p8 §12 | mandatory | Avoid one do-everything prompt; limit retries, debate rounds and spending. | Limits configured. | test | unimplemented |

## M4

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M04-002 | Desc p3 §4 | mandatory | Scouts run scheduled (CronJob) and on demand. | Both triggers demonstrated. | demo | in_progress |
| M04-003 | Desc p3 §4 | mandatory | Per-source rate limits and failure handling. | Rate limit and failure tests pass. | test | implemented |

## M5

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| SEC-001 | Desc p1 §1.3 | mandatory | Keep no private data. | Stored cards contain only public idea data. | inspection | unimplemented |
| ARC-007 | Desc p2 §3 Fig.1 | mandatory | Scouts reach the internet only through M5. | NetworkPolicy test proves only M5 egress. | infra-test | implemented |
| M05-001 | Desc p3 §4 | mandatory | M5 is the single controlled exit to the internet with connectors, domain allow-list, rate limits, robots.txt handling and cache. | Disallowed domain or robots path refused; cache used. | test | implemented |
| M05-002 | Desc p3 §4 | mandatory | M5 sanitiser strips instructions aimed at models. | Poisoned page test passes. | security-test | implemented |
| M05-003 | Desc p3 §4 | mandatory | A NetworkPolicy ensures only M5 reaches the internet. | Non-M5 pod egress fails; M5 egress works. | infra-test | implemented |
| ETH-002 | Guide p4 §5 | mandatory | Per-domain rate limits, clear User-Agent, caching, back-off on errors. | Tests for each. | test | implemented |

## M6

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| ARC-003 | Desc p2 §3 Fig.1 | mandatory | M7, M8 and M9 read from and write to M6; M6i feeds M6; M4 feeds M6i. | Data paths implemented as drawn. | inspection | unimplemented |
| ETH-003 | Guide p4 §5 | mandatory | No logins and no private data; keep only what an idea card needs. | Field review. | inspection | unimplemented |

## M8

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| CMN-007 | Guide p8 §12 | mandatory | Ideas must not be renamed copies of existing products or ignore the student's hours. | Duplicate and hours checks. | test | unimplemented |

## M9

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| RUB-001 | Guide p7 §10 | mandatory | One versioned rubric file per dimension with an anchor for every score 0 to 5, at least one worked example per level, features and output schema. | Six rubric files validate. | contract | implemented |

## M10

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| ARC-005 | Desc p2 §3 Fig.1 | mandatory | M10t is offline and supplies the model to M10. | Model artefact produced offline and loaded by M10. | inspection | unimplemented |
| M10-004 | Desc p4 §4 | mandatory | Fallback to a hosted model. | Invalid or unavailable local model falls back and logs. | test | unimplemented |
| FT-007 | Guide p4 §6.2 | mandatory | Serve in own container behind /score, /health, /ready; no large weights in git (release asset or registry); requests and limits from measurements. | Container serves; weights outside git. | infra-test | unimplemented |
| FT-008 | Guide p4 §6.2 | mandatory | Validate every output against schema; invalid: retry once, then fall back to hosted model and log it. | Retry-then-fallback test. | test | unimplemented |

## M10t

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| FT-011 | Guide p4 §6 | recommended | Goal is a cheaper, faster, more consistent model that follows rubric format and evidence rule. | Comparison discusses cost, speed, consistency. | inspection | unimplemented |

## M11

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| ARC-004 | Desc p2 §3 Fig.1 | mandatory | M9 sends scores via M10 to M11; M11's verdict goes to M12. | Scores flow to M11; verdict passes critic/guardrail path. | inspection | unimplemented |
| VAL-006 | Desc p3 §3.2 Fig.3 | mandatory | The language model gives scores with evidence; only the Verdict Engine decides the verdict. | No model output can set a verdict. | test | unimplemented |
| M11-001 | Desc p4 §4 | mandatory | Verdict Engine turns six scores into a verdict by fixed rules; plain code with no LLM. | No model dependency in M11. | inspection | implemented |
| M11-002 | Desc p4 §4 | mandatory | Same input gives same output. | Determinism test passes. | unit | implemented |
| M11-003 | Desc p4 §4 | mandatory | Rules are in a ConfigMap. | Changing ConfigMap changes thresholds without rebuild. | infra-test | implemented |
| VER-001 | Desc p4 §5 | mandatory | The language model never outputs the verdict; M11 is deterministic and unit-tested; it is decision support, not a success prediction. | UI wording and code satisfy this. | inspection | in_progress |
| CMN-003 | Guide p8 §12 | mandatory | No model may decide or adjust the verdict. | Only M11 writes verdicts. | test | implemented |

## M12

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M12-002 | Desc p4 §4 | mandatory | Injection defence: fetched text is data. | Injection fixtures have no effect. | security-test | unimplemented |
| M12-003 | Desc p4 §4 | mandatory | Input rail on user input. | Disallowed input blocked. | security-test | unimplemented |
| ETH-005 | Guide p4 §5 | mandatory | Fetched text is data; never obey instructions in it. | Poisoned page test. | security-test | unimplemented |
| CMN-004 | Guide p8 §12 | mandatory | No score or claim without evidence id; no competitor absent from the knowledge base. | Validation rejects both. | test | unimplemented |

## M13

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| ARC-006 | Desc p2 §3 Fig.1 | mandatory | All modules send telemetry to M13. | Traces from every module appear under a run id. | test | unimplemented |
| SUB-008 | Desc p6 §6.3 | mandatory | Screenshots: a trace, dashboard, drift report, retrieval result and fine-tuning comparison. | Captured and captioned. | evidence | unimplemented |
| OPS-006 | Guide p5 §7 | mandatory | Evaluation runs as a Kubernetes Job and nightly from Jenkins. | Both runs shown. | demo | unimplemented |
| K8S-009 | Guide p6 §9 Fig.3 | mandatory | Traces to stdout as JSON lines and to a trace volume; metrics endpoint; dashboard; cost per verdict. | Observable in cluster. | demo | unimplemented |

## M14

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| GEN-004 | Desc p1 §1.1 | mandatory | Complete product: web interface, multi-agent backend, RAG knowledge base, fine-tuned scoring model, AgenticOps, and a delivery pipeline that builds, tests and deploys everything on Kubernetes. | All named parts run on the cluster from the pipeline. | demo | unimplemented |
| GEN-005 | Desc p1 §1.2 | mandatory | Required technology: GitHub, GitHub Actions, Jenkins, Docker, Kubernetes, RAG, fine-tuning, AgenticOps. | Each technology has working evidence. | inspection | unimplemented |
| GEN-006 | Desc p1 §1.2 | mandatory | The whole system runs on Kubernetes, one container per module. | Every module has its own container running in the cluster. | demo | in_progress |
| COL-001 | Desc p1 §1.3 | mandatory | Group of 2; both members commit code. | Git history shows meaningful commits from both members. | git-history | unimplemented |
| COL-002 | Desc p1 §1.3 | mandatory | Both members review each other's pull requests. | Each member has genuine reviews on the other's PRs. | git-history | unimplemented |
| COL-003 | Desc p1 §1.3 | mandatory | Both members must be able to explain the whole system. | Viva preparation completed by both. | viva | unimplemented |
| DOC-001 | Desc p1 §1.3 | mandatory | AI tools are allowed; students are responsible for every line and keep an AI-usage log of what AI wrote, what they changed and why. | AI-usage log is current and accurate. | inspection | unimplemented |
| SEC-002 | Desc p1 §1.3 | mandatory | Never commit keys or passwords. | Secret scan passes on every PR. | ci | unimplemented |
| M14-001 | Desc p4 §4 | mandatory | GitHub with protected main and pull requests. | Protection verified through GitHub API. | inspection | implemented |
| M14-002 | Desc p4 §4 | mandatory | GitHub Actions on every pull request. | Workflow runs on each PR. | ci | unimplemented |
| M14-003 | Desc p4 §4 | mandatory | Jenkins for delivery. | Jenkins deploys merged code. | demo | implemented |
| M14-004 | Desc p4 §4 | mandatory | One Docker image per module. | Image list covers every module. | inspection | implemented |
| M14-005 | Desc p4 §4 | mandatory | Full Kubernetes deployment with rollout and rollback. | Rollout and rollback demonstrated. | demo | unimplemented |
| SUB-001 | Desc p6 §6.1 | mandatory | Submit through GCR a GitHub repository link containing code, Dockerfiles, workflows, Jenkinsfile, k8s/, fine-tuning data and scripts, rubrics, evaluation sets and a README that lets someone else start the system. | Checklist complete. | inspection | unimplemented |
| SUB-002 | Desc p6 §6.1 | mandatory | The people marking can open the repository. | Access verified from a signed-out browser or grant. | inspection | unimplemented |
| SUB-003 | Desc p6 §6.2 | mandatory | Report is a PDF of at most 10 pages excluding screenshots. | Page count <=10. | inspection | unimplemented |
| SUB-004 | Desc p6 §6.2 | mandatory | Report sections: summary and changes from architecture; modules and architecture figure; verdict design with before/after confusion matrix and a worked example; knowledge base; fine-tuning with comparison table and one failure case; AgenticOps results; platform incl. how requests and limits were measured; known limits and next steps. | All sections present with real data. | inspection | unimplemented |
| SUB-005 | Desc p6 §6.3 | mandatory | Screenshots with one-line captions: protected main and PR with required checks; merge-conflict PR; green and failing Actions runs; green and failing Jenkins runs. | Captured and captioned. | evidence | unimplemented |
| SUB-006 | Desc p6 §6.3 | mandatory | Screenshots: all pods running; a rollout and rollback; NetworkPolicy test. | Captured and captioned. | evidence | unimplemented |
| SUB-009 | Desc p6 §6.4 | mandatory | AI-usage log and at least 3 short design decision records (templates in Guide Section 11). | >=3 records and log submitted. | inspection | unimplemented |
| SUB-010 | Desc p6 §6.5 | mandatory | Contribution table signed by both members, matching git history. | Signed by both; consistent with history. | inspection | unimplemented |
| IFC-001 | Guide p1 §1 | mandatory | Guide field lists and numbers are minimums; module names M1 to M14 are shared. | No documented minimum is dropped. | contract | unimplemented |
| IFC-002 | Guide p1 §2 | mandatory | All modules exchange JSON; define each schema once, validate every input and output, keep schema files in the repository. | Shared schemas validated at every boundary. | contract | unimplemented |
| API-001 | Guide p2 §3 | mandatory | Names may differ if documented but every capability must exist. | Capability map documented. | inspection | unimplemented |
| API-002 | Guide p2 §3 | mandatory | Every service exposes /health (process alive) and /ready (can serve now). | Both endpoints on every service. | test | implemented |
| REP-001 | Guide p3 §4.1 | recommended | Repository layout: README, docs, services, jobs, rubrics, config, eval, k8s, workflows, Jenkinsfile, docker-compose.yml. | Layout present. | ci | unimplemented |
| REP-002 | Guide p3 §4.1 | mandatory | Services may be grouped differently but each module is its own deployable unit with its own Dockerfile. | Dockerfile per module. | ci | implemented |
| GIT-001 | Guide p3 §4.2 | mandatory | Create repository on day 1; protect main: no direct pushes, PRs only, required status checks, one review from the other member. | Verified protection settings. | inspection | implemented |
| GIT-002 | Guide p3 §4.2 | mandatory | One issue per task linked to its PR; small single-purpose branches. | PRs link issues. | git-history | unimplemented |
| GIT-003 | Guide p3 §4.2 | mandatory | Conventional commits. | Commit messages conform. | ci | unimplemented |
| GIT-004 | Guide p3 §4.2 | mandatory | Create one deliberate merge conflict, resolve it in a PR and keep the screenshot. | PR and screenshot exist. | evidence | unimplemented |
| SET-001 | Guide p3 §4.3 | mandatory | Local Kubernetes (kind, minikube or k3d) whose network plugin enforces NetworkPolicy. | Enforcement proven. | infra-test | implemented |
| SET-002 | Guide p3 §4.3 | mandatory | docker-compose.yml for development only (Postgres, Redis, vector store, services); deployment target is Kubernetes. | Compose brings up dependencies. | demo | implemented |
| SET-003 | Guide p3 §4.3 | mandatory | Settings in environment variables or ConfigMaps; commit .env.example with names and no secrets. | Example file has no values. | ci | in_progress |
| SET-004 | Guide p3 §4.3 | mandatory | README lets a new person start the system with a short list of commands. | Fresh-machine walkthrough succeeds. | demo | in_progress |
| DKR-001 | Guide p3 §4.4 | mandatory | One image per module, at least 6 distinct images. | >=6 distinct images, one per module. | ci | implemented |
| DKR-002 | Guide p3 §4.4 | mandatory | Images are multi-stage, non-root, with pinned versions and a .dockerignore. | Static checks pass. | ci | in_progress |
| DKR-003 | Guide p3 §4.4 | mandatory | Images tagged by commit SHA (never only latest) and scanned in CI. | Tags use SHA; scan job passes. | ci | implemented |
| CIC-001 | Guide p5 §8 Fig.2 | mandatory | Feature-branch PR runs GitHub Actions; merge needs all green; Jenkins runs after merge and nightly. | Flow demonstrated. | demo | in_progress |
| CIC-002 | Guide p5 §8.1 | mandatory | Every PR: lint and type checks; unit tests including Verdict Engine; UI component tests. | Jobs run. | ci | unimplemented |
| CIC-004 | Guide p5 §8.1 | mandatory | Docker build and image scan. | Jobs run and block on critical findings. | ci | unimplemented |
| CIC-005 | Guide p5 §8.1 | mandatory | Kubernetes manifest validation. | Job runs. | ci | unimplemented |
| CIC-006 | Guide p5 §8.1 | mandatory | All PR checks are required checks on main. | Protection lists them. | inspection | unimplemented |
| JNK-001 | Guide p5 §8.2 | mandatory | Jenkinsfile stages: checkout, build and tag by commit SHA, push, deploy to test cluster, smoke test, nightly full evaluation compared with stored baseline. | All stages run. | demo | in_progress |
| JNK-002 | Guide p5 §8.2 | mandatory | A failure stops the pipeline and nothing is deployed; rollback uses kubectl rollout undo. | Failing run shown; rollback shown. | demo | implemented |
| JNK-003 | Guide p5 §8.2 | mandatory | Jenkins runs in a container with Docker and cluster access; kubeconfig is a Jenkins credential, never in the repository. | No credential in repo. | inspection | implemented |
| JNK-004 | Guide p6 §8.2 | mandatory | Use SCM polling (e.g. every 2 minutes) or a tunnel since webhooks cannot reach a laptop. | Trigger configured. | inspection | implemented |
| K8S-001 | Guide p6 §9 Fig.3 | mandatory | Namespace idea-validator with Ingress as single entry point; stateless Deployments; postgres and vector-store PVCs and redis. | Objects present. | infra-test | implemented |
| K8S-002 | Guide p6 §9.1 | mandatory | Deployments and Services for M1, M3, M5, M6, M7, M8 and M9, M10, M11, M12, M13. | Each listed module deployed. | infra-test | implemented |
| K8S-003 | Guide p6 §9.1 | mandatory | CronJobs for scouts (hourly or daily) and ingestion with freshness check; Job for evaluation; fine-tuned model import job (Fig.3). | Objects run. | infra-test | in_progress |
| K8S-004 | Guide p6 §9.1 | mandatory | ConfigMaps for weights, thresholds, floors, rubric versions, budgets; Secrets for API keys and DB password. | Config separated from secrets. | inspection | unimplemented |
| K8S-005 | Guide p6 §9.1 | mandatory | Liveness and readiness probes on every service; requests and limits from measurements (kubectl top). | Measurement record backs each limit. | inspection | unimplemented |
| K8S-006 | Guide p6 §9.1 | mandatory | Autoscaler on the API gateway. | HPA scales under load. | demo | unimplemented |
| K8S-007 | Guide p6 §9 Fig.3 | mandatory | Rollout: RollingUpdate with maxUnavailable 0; kubectl rollout undo demonstrated. | Zero-unavailable update and rollback. | demo | in_progress |
| K8S-008 | Guide p6 §9 Fig.3 | mandatory | Every workload: probes, measured requests and limits, non-root, pinned image. | Manifest policy passes. | ci | in_progress |
| NET-001 | Guide p7 §9.3 | mandatory | Default-deny egress for the namespace; allow DNS, traffic between services, and internet egress only for M5 pods selected by label. | Policies applied and tested. | infra-test | implemented |
| NET-002 | Guide p7 §9.3 | mandatory | Network plugin enforces NetworkPolicy (e.g. Calico or Cilium). | Enforcement proven. | infra-test | implemented |
| DDR-001 | Guide p8 §11.1 | mandatory | At least 3 design decision records, one page or less, in docs/decisions/, with Title, Status, Context, Options, Decision, Why, Cost, AI use. | >=3 conforming records. | inspection | unimplemented |
| LOG-001 | Guide p8 §11.2 | mandatory | AI-usage log columns: Date, Tool, What you asked for, What you changed, Why. | Columns present. | ci | unimplemented |
| LOG-002 | Guide p8 §11.2 | mandatory | Contribution table: modules owned, PRs authored/reviewed, approximate hours, signature, for both members with name and roll number. | Template complete and signed by students. | inspection | unimplemented |
| CMN-008 | Guide p8 §12 | recommended | Get a thin end-to-end version on Kubernetes (with Docker and Jenkins) early, then improve. | Walking skeleton in Phase 1. | demo | implemented |
