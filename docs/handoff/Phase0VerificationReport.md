# Phase 0 verification report

**Status: PHASE 0 PARTIALLY COMPLETE — BLOCKERS REQUIRE RESOLUTION** (2026-11-28)

Remaining blocker at the time of the first commit: independent review and human approval of the promotion PR.

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
| harness-tests | 27 of 27 |
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
Branch protection and rejection probes: `docs/evidence/phase0/github-protection.md`. Workflow results: see the
pull request checks.

## Not verified
Jenkinsfile syntax and execution; NetworkPolicy enforcement; hooks in a freshly started session of the second
clone; secondary review; promotion approval.

## Application code
None.
