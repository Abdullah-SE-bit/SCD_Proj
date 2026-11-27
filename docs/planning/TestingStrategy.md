# Testing strategy

Operational today: harness negative tests, contract tests, manifest validation, lint, types, secret and
dependency scans. Everything below activates with the code it tests.

| Level | Scope | Tool | CI check | Applies from |
|---|---|---|---|---|
| Unit | verdict engine, features, dedupe, budgets | pytest | verdict-unit-tests, backend-unit-tests | P01 / P03 |
| Component | UI screens and states | Vitest + Testing Library | ui-component-tests | P01 |
| Integration | services with Postgres, Redis, vector store | pytest + compose | backend-unit-tests | P02 |
| Contract | schemas, OpenAPI, provider and consumer examples | jsonschema | contract-tests | now |
| End to end | J1-J7 browser journeys | Playwright | added in P05 | P05 |
| Security | injection, poisoned page, auth, limits, egress | pytest, netpol script | backend-unit-tests, evidence | P04 |
| Infrastructure | manifests, images, policy enforcement | kubeconform, Trivy | k8s-validate, docker-build, image-scan | now / P01 |
| Retrieval | recall@5, MRR on 20+ queries | pytest | retrieval-gate | P04 |
| Behaviour | invalid scorer JSON, tool timeout, empty source, poisoned page | replayed responses | agent-behaviour-tests | P05-P08 |
| Model and verdict evaluation | see EvaluationStrategy | harness | nightly | P06-P09 |
| Performance | latency, resource use | kubectl top, load script | evidence | P10 |

Rules: a check never passes without running its tests; zero collected tests is a failure; no live model in CI.
