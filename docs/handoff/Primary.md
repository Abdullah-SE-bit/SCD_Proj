# Handoff: primary (Abdullah-SE-bit)

- Current task: Phase 0 close-out.
- State: foundation on `main` (`08cb1c3`). Rules A-06 and A-07 are in force (#19, #20). P00.01 to P00.06 and the
  P00 gate are recorded `done` by the gate pull request.
- Next: promotion `dev` → `main`, approved by the `Demidoga` account owner. Then stop: Phase 1 needs the project
  owner's authorisation and the decisions in `PendingDecisions.md`.
- Final promotion #22: `main` still judges with the earlier rules, so each record now names its review.
- Rules: no review into `dev`; merge conflict-free pull requests; review only into `main`.
- Processed message ids: 20261128-secondary-001 to 20261128-secondary-010.
- Correction: the P00.01 record cited the #16 approval, which did not review that task; it now cites #8.
- Correction: the P00.04 record now cites the #15 approval of the harness fixes instead of the one-line #17.
- Owner removed the authorization label requirement.

## P01.02 (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/166)
- Done: 12 service and 3 job skeletons, one image each; probes and image rules tested.
- Not done: `gateway` and `ui` (P01.03); readiness has no dependencies yet; module requirements are not audited.
- Decision: standard-library services (`services/README.md`); decision record due with the P01 gate.
- The harness replan was dropped: the existing registry stays; issues follow it.
- Next: P01.04 once P01.01, P01.02 and P01.03 are merged.

## P01.04 (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/209)
- Done: everything deploys with `scripts/deploy.sh`; smoke test passes and fails when a service is removed; compose
  data stores, gateway and UI start. Recorded `in_review`.
- Not done: measured requests and limits, `rollout undo` demonstration, second-machine walkthrough.
- Cluster `idea-validator` is running; namespace `ingress` holds Traefik.
- Open question to the owner: `CLAUDE.md` still asks for a label on `done` records.
- Next: P01.05 (secondary), then the P01 gate.

## P01 gate
- Demonstrated on `dev` c808e99: smoke test, network policies, browser card (`docs/evidence/screenshots/p01-gate-verdict-card.png`), Jenkins build 5.
- P01.01 to P01.05 recorded `done`. The browser showed fixture data only; nothing is evaluated yet.
- Open: nightly evaluation, measured resources, rollback demonstration on `dev`, second-machine walkthrough.
- Jenkins is stopped. Next: Phase 2 (P02.01) and Phase 3 (P03.01, P03.03).

## P03.01 (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/214)
- Done: gates, score, confidence, thresholds, floor, abstention, `/verdict`, rules ConfigMap shown live.
- Not done: sensitivity, challenge, what-if (P03.02). Gate facts wait for the scorers (P05.01).

## P04.01 (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/215)
- Done: `/fetch` and `/llm`; egress proven on the cluster.
- Not done: no live model call (needs the API key and model name in `.env`, then `scripts/load_secrets.sh`).

## P03.02 (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/217)
- Done: challenge adjustments, sensitivity, suggestions, `/whatif`; worked example reproduced.
- Open: AMB-24 (flip count) for the instructor; applying a suggestion arrives with the run workflow.

## P04.02 (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/219)
- Done: three connectors, on demand and CronJob; live run 679 Hacker News and 1000 GitHub items.
- Open: Product Hunt needs `PRODUCT_HUNT_TOKEN` in `.env`, then `scripts/load_secrets.sh` and one more run. Recorded
  `in_review` until then. Deployment wiring for profile database settings and the gateway signing key is still open.

## P02.03 (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/220)
- Done: history, versions, comparison, cache with visible hits.
- Open: cluster wiring for profile database, Redis, migrations and gateway signing key (no unblocked task covers
  `k8s/`); not run against real Redis or PostgreSQL.

## Cluster wiring fix (https://github.com/Abdullah-SE-bit/SCD_Proj/pull/224)
- Accounts, profile, history, cache and search work on the cluster (`docs/evidence/P01.04-wiring.txt`).
- The notes in the profile, kb and ingestion READMEs saying `k8s/` passes no settings are now out of date.
- The scheduled ingestion CronJob has not been run on its own.
