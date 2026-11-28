# Handoff: secondary (Demidoga)

## Current: P02 gate recorded with a stated limit (2026-11-28)
- [Demonstration](../evidence/phase2/gate-demo.txt) on the cluster at `dev` `7e42f3e` ([script](../evidence/phase2/gate-demo.py)).
- Holds as a user action: register, log in (wrong password refused), save and edit the profile, history page answers.
- **Limit:** history has content only because records were written to the profile service by hand. No public
  route saves an idea; the Validate flow (P05) must. Show history again with a user-saved idea then.
- Recorded `done` on the account owner's decision (A-10).
- P02.04 merged as #223 (`5091cd7`). The cluster is no longer in use by this session.

## Earlier: P02.04 profile and history screens (2026-11-28)
- [#223](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/223) from `feat/P02.04-screens`. Status: `done`.
- [Profile](../evidence/screenshots/ui-profile.png), [history and comparison](../evidence/screenshots/ui-history-compare.png)
  (fixture ideas seeded through the profile service; no public route creates ideas yet).
- P04.04 merged as [#222](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/222), `in_review`.
- Waiting: **P04.05** for 20 or more hand-written queries (human). **P02 gate** for the cluster to get database
  settings, migrations and the signing key (`k8s/`, not this account's scope). **P05.01** for the P04 gate.
- Next: report to the primary session.

## Earlier: P04.04 hybrid search and reranking (2026-11-28)
- [#222](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/222) from `feat/P04.04-retrieval`. Status: `in_review` (P04.03 is in review).
- Done: `POST /search`, `GET /coverage`; [searches on the cluster](../evidence/phase4/search.txt).
- **Open, deployment:** the `kb` Deployment needs database settings (as in
  [kb-pod.yaml](../evidence/phase4/kb-pod.yaml)) and about 1.5 GiB.
- **For P04.05:** `Search.query(text, filters, hybrid=..., reranked=...)` measures each step. It needs 20 or more
  hand-written queries with relevant card ids (human work, H2).
- **For P05.01:** call `POST /search`; each item's `evidence_id` is what a score cites.
- Merged as #222 (`83a3e78`).

## Earlier: P04.03 ingestion (2026-11-28)
- [#221](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/221) from `feat/P04.03-ingestion`. Status: `in_review`.
- Done: 1,667 cards (GitHub 1000, Hacker News 667), 1,748 chunks indexed, snapshot on volume `raw-items`
  (`snapshot/cards.jsonl`), rerun adds nothing, restore into an empty database;
  [counts](../evidence/phase4/ingestion-counts.txt).
- **Open:** the third source (M6I-003). Product Hunt needs a working token; then one scouts run and a re-ingest.
- **Open, deployment:** the `ingestion` CronJob passes no database settings, volume, snapshot path or memory
  (1 GiB limit used), and `k8s/` still expects the old small image. Apply `ingestion-job.yaml` to run it.
- **For P04.04:** collection `chunks` (384, cosine), payload `chunk_id, card_id, text, date, source, niche, url`;
  cards as JSON in table `cards.document`; embed queries with `scd_ingestion/embed.py`'s model.
- Merged as #221 (`3f195c9`).
- Messages: primary session, 2026-11-28: cluster and `raw-items` are this session's until it says it is done.

## Earlier: P02.02 accounts, limits and profile API (2026-11-28)
- [#218](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/218) from `feat/P02.02-auth`. Status: `done`.
- Done: register, login, tokens, rate limits, validation, profile read and update;
  [evidence](../evidence/phase2/accounts-http.txt). Settings and limits: `services/gateway/README.md`.
- **Open, deployment:** the cluster and compose pass no database settings to `profile`, no `JWT_SIGNING_KEY` to the
  gateway, and nothing runs the migration, so account routes answer 503 there.
- **For P02.04:** `POST /auth/login` returns a token; send it as `Authorization: Bearer`. Once the UI signs in,
  `/validate` can require it (the smoke test must then log in).
- Merged as #218 (`7207f49`).

## Earlier: P02.01 migrations and repositories (2026-11-28)
- [#216](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/216) from `feat/P02.01-migrations`. Status: `done`.
- Done: M2 tables, `python -m scd_profile.migrate`, repositories and services;
  [evidence](../evidence/phase2/m2-migrations.txt).
- **For P02.03:** build on `scd_profile/repositories.py` (`versions_of`, `verdicts_of`, `scores_of`) and
  `ProfileService`. Tests get a migrated database from `services/profile/conftest.py`.
- **Open, deployment:** `k8s/apps.yaml` and compose pass no database settings to `profile` and nothing runs the
  migration in the cluster (outside this task's scope).
- Merged as #216 (`419158c`).

## Earlier: P03.03 rubrics (2026-11-28)
- [#213](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/213) from `feat/P03.03-rubrics`. Status: `in_review`.
- Done: six version 1 rubrics in `rubrics/` (JSON) with a validation test;
  [test output](../evidence/phase3/rubric-tests.txt).
- **Open, human:** both members review anchors and examples and record it in `rubrics/README.md`. The P03 gate needs
  this task `done`.
- **Open, code:** CI does not run `rubrics/test_rubrics.py`. A test under `tests/` or a scorer test (P05.01) can.
- Worked examples are invented illustrations: do not use them as training or evaluation data.
- Merged as #213 (`6e61537`).
- Messages: primary session, 2026-11-28: P01 gate merged; order P03.03, P02.01, P02.02, P02.04, P04.03 to P05.01.

## Earlier: P01.05 Jenkins delivery (2026-11-28)
- [#211](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/211) from `feat/P01.05-jenkins-pipeline`. Status: `in_review`. It replaces #210, where
  gitleaks read plugin version pins as API keys (false positives; pins moved to `plugins.yaml`).
  The scan reads every branch, so it kept failing until the owner deleted the #210 branch (2026-11-28).
  A fourth build, on that branch's last commit with the final setup script and pinned plugins, passed.
- Start: `sh scripts/jenkins_up.sh` (after `cluster_up.sh`); stop: `docker stop scd-jenkins scd-registry`.
  See [CI/CD](../devops/CICDArchitecture.md).
- Evidence: [three builds](../evidence/phase1/jenkins-runs.txt) (green; deliberate failure with rollback; started by
  polling), [stage view](../evidence/screenshots/jenkins-green.png), [rollback](../evidence/screenshots/jenkins-fail.png).
- Not done: builds shown are of the task branch, not of merged code; nightly evaluation (P08.02); GHCR (needs the
  owner's token); rollback leaves ConfigMaps, replica counts and the CronJob image.
- The cluster now runs images from the local registry, so `scd-registry` must be running when pods are recreated on a
  node that has not cached them. `scripts/deploy.sh` still works without it.
- Merged as #211 (`c808e99`); the P01 gate recorded it `done`.
- Messages: primary session released the cluster for this task (2026-11-28).

## Earlier: P01.03 thin UI and gateway path
- Merged as [#208](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/208) (`3191a00`), recorded `in_review`.
- Evidence: [one image, two API addresses](../evidence/phase1/ui-runtime-api.txt),
  [screenshot](../evidence/screenshots/ui-fixture-card.png). The gateway does not call the orchestrator yet.
- gateway: port 8000, `PORT` optional. ui: port 8080, `API_URL` required, read at start by nginx.

## Earlier: P01.01 cluster with enforced NetworkPolicy
- Merged as [#189](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/189) (`afd1bf8`), recorded `in_review`.
- `scripts/cluster_up.sh`, `scripts/netpol_test.sh`;
  [test output](../evidence/phase1/netpol-test.txt). Not shown: real M5 or UI workloads, ingress rules.
- Label pods `app: <module>`. The cluster maps no host ports (`extraPortMappings` is needed for Ingress from the host).
  Run-time downloads outside M5 are blocked.
- This PC: the `idea-validator` cluster was left running; the kubectl context is `kind-idea-validator`.

## Earlier: P00.06 independent review
Kept because `status/P00.06.json` cites this file. The statements below describe the state at that time.

- Task: P00.06 independent review. Review finished; task **not recorded done** (see "To record `done`").
- State (2026-11-28): [#8](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8)
  [approved](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8#pullrequestreview-6094108280) at `b5d038a` and merged
  into `main` as `08cb1c3` (merge commit, no admin override). `main` files equal the approved head.
- The first round on #8, at `b1f4081`:
  [findings](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8#pullrequestreview-6093185832),
  [change request](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8#pullrequestreview-6093195416).
- Every decision here was Asad's, after being shown Claude's recommendation or a summary. Claude Code did the
  analysis, wrote the review text and submitted it (and the merge). The reviews do not claim a line-by-line human
  review.

### Reviews of the fix pull requests (all merged into `dev`)
| PR | Decision and head |
|---|---|
| #12 | [changes requested](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/12#pullrequestreview-6093453303) `7089562`; [approved](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/12#pullrequestreview-6093631448) `dcedbbe` |
| #13 | [approved](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/13#pullrequestreview-6093456087) `3481259` |
| #14 | [approved](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/14#pullrequestreview-6093456346) `ee6e074`; GitHub shows this approval as **dismissed**. Merged at `be5c3b6`, which adds the `dev` merge; its hand-resolved conflicts were in the primary handoff and AI-usage log. No new approval was given. |
| #15 | changes requested [`7b1a757`](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/15#pullrequestreview-6093453641) and [`6b3c8e9`](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/15#pullrequestreview-6093630925); [approved](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/15#pullrequestreview-6093835146) `58c5c12` |
| #16 | [approved](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/16#pullrequestreview-6093959112) `e9bd4d0` (local suite finished afterwards: 20/20) |

#11 (the first record) was merged by the primary account at `a02e08d`, which adds the `dev` merge with the
AI-usage log conflict resolved on that side. GitHub shows its approval of `f361fcb` as dismissed before the merge,
and no later approval.

### Close-out defect: fixed
Recording `done` regenerates `ImplementationPlan.md`, which was outside the scope of the P00.04, P00.05 and P00.06
branches, so those records and the gate could not pass. This corrected the #16 review, which tested only P00.02;
the #15 reviews missed it. [#17](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/17) fixes it:
[approved](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/17#pullrequestreview-6094241289) at `a71a8b6`, merged into
`dev` as `6cb5e5c`. On that head and on a simulated closed Phase 0, `scd.py all` passed 20/20.

### To record `done` (simulated end to end)
- One pull request per task, opened by its owner, one at a time (parallel ones conflict), then the `P00` gate, which
  needs P00.01-P00.06 already `done` on `dev`.
- Each carries `status/<ID>.json` (`done`, `pr`, `evidence`, `reviewed_by` not the owner, `review`), the owner's
  handoff, the AI-usage log, the regenerated plan and a human's `authorized-protected-change` label.
- The checker only tests that `review` is a link into this repository: each must be a real review by `reviewed_by`.
- P00.06 needs a review by `Abdullah-SE-bit` of this account's work. The one on #11 is dismissed.
- Promote the gate record to `main` before any application code reaches `dev`, or that promotion fails.

### Open then
- `DefinitionOfDone.md` still says a phase gate pull request sets `done`.
- Low findings: [ReviewResponses](ReviewResponses.md).
- During the #12 review a rollback test wrongly called the real `kubectl` (`rollout undo` and `scale` for
  `model-server`, context `minikube`). Every call failed to connect; nothing changed. The test was rerun with a
  fake `kubectl` and no reachable cluster.

### Messages (P00.06)
- Processed: `20261128-primary-001` to `20261128-primary-009`.
- Sent: `20261128-secondary-001` to `20261128-secondary-010`.
