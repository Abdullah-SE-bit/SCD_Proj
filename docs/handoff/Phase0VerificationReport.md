# Phase 0 verification report

**Status: Phase 0 is complete once this report is on `main`**, which takes a promotion with the other
collaborator's approval. Until then it is partially complete. Phase 1 is not authorised.

## Local checks (Windows, Python 3.12)
`scd.py all`: 20 of 20 passed.

| Check | Result |
|---|---|
| repo-structure | 94 required files, 21 CI job names |
| requirements-registry | 237 requirements, 16 modules, U1-U10 |
| traceability | 237 requirements mapped to 55 tasks |
| task-policy, protected-files | pass |
| branch-policy | pass locally (not a pull request) |
| secret-scan (built-in) | 207 files |
| harness-tests | 43 of 43 at close-out (27 at the first version) |
| lint, typecheck | pass |
| contract-tests | 10 schemas, 20 examples, 7 OpenAPI documents |
| k8s-validate | 5 resources valid |
| dependency-security | pip-audit and bandit clean |
| verdict-unit-tests, backend-unit-tests, ui-component-tests, retrieval-gate, agent-behaviour-tests, docker-build, image-scan | NOT APPLICABLE: no application code |

`ci-gate` runs only on GitHub.

## Harness observed live
Project hooks loaded into the authoring session as soon as `.claude/settings.json` existed and denied edits to
`harness/verification/scd.py` until the project owner enabled maintenance mode. The session did not work around
the denial.

## Defects found and fixed (owner enabled maintenance mode for this)
1. Identity check expected `--user LOGIN;` while the real credential helper has `--user LOGIN)`, which would
   have denied every commit. The test fixture hid it; the fixture now uses the real shape (failing before the fix).
2. `harness/policies/required-files.json` was missing.
3. A crashing check aborted `scd.py all`; it now reports a failure and continues.
4. `harness/tests/**` was not protected.

Design note: the harness takes effect in the session that creates it, with no bootstrap exemption.

## GitHub behaviour
Branch protection and rejection probes: `docs/evidence/phase0/github-protection.md`.
[First workflow run](https://github.com/Abdullah-SE-bit/SCD_Proj/actions/runs/46063115027) on [PR 7](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/7): all 21 checks passed, including actionlint, the gitleaks
history scan and kubeconform.

## Pull requests
- [#7](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/7) bootstrap → dev: 21/21, merged as `13b0df2`.
- [#8](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8) dev → main: promotion, awaiting independent review and approval.
- [#9](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/9) wrong-target probe: failed as expected, closed. See
  `docs/evidence/phase0/ci-negative-tests.md`.

## Harness cases and how each was verified
| Case (Phase 0 instruction §28) | Local test | On GitHub |
|---|---|---|
| wrong identity, wrong repository | yes | - |
| direct work on main or dev | yes | direct push rejected |
| incorrect PR target | yes | #9 |
| blocked task, duplicate claim | yes (real bare remote) | - |
| unauthorised file change, protected specification | yes; observed live in session | - |
| committing secrets | yes | gitleaks and push protection active, no secret pushed to test them |
| invalid contract, missing acceptance, missing handoff | yes | - |
| failing or skipped required checks | yes | #9 |
| premature completion, application code in Phase 0 | yes | - |

## Independent review rounds
| Round | Result |
|---|---|
| #8 at `b1f4081` | changes requested: 7 high, 10 medium, low items |
| #12 to #15, first review | #13, #14 approved; #12, #15 changes requested |
| second | #12 approved; #15 changes requested (one item) |
| third | #15 approved at `58c5c12` |

All decisions were made on the `Demidoga` account in the secondary session with AI-written analysis. The
statements above about 27 tests describe the first foundation; the harness has 41 tests after the fixes.
Responses: [ReviewResponses](ReviewResponses.md).

## Promotion
#8 was approved at `b5d038a` ([review](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8#pullrequestreview-6094108280)) and merged into `main` as
`08cb1c3`; the merged tree equals the approved head. `scd.py all` passed 20/20 and GitHub 21/21 on that head.
The decision was given in the secondary session; the review text states it is AI-assisted.

## Close-out defect
Found during the #8 review and reproduced by `test_phase_can_be_closed_task_by_task`: P00.04 to P00.06 could
not record `done`, which also blocked the gate. Fixed by allowing the generated implementation plan in every
task pull request (`repo-structure` rejects hand edits to it).

## Close-out
All six tasks and the gate are recorded `done` in one pull request (decision A-06: no review into `dev`),
labelled by the owner. P00.06 evidence includes the findings, the approval of #8 and the primary approval of
the secondary's record (#18).

Later changes: #19 and #20 introduced the owner's merge and review rules. The automated security review noted
that merges are no longer confirmed locally (intended; `main` is protected on GitHub) and that completion records
had lost their human label (restored before #20 merged).

## Not verified
Jenkinsfile syntax and execution; Docker builds and image scan; NetworkPolicy enforcement and rollback on a
real cluster; a human line-by-line audit of the requirements.

## Application code
None.
