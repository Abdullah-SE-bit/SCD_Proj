# Handoff: secondary (Demidoga)

## Current: P01.01 cluster with enforced NetworkPolicy (2026-11-28)
- [#189](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/189) from `feat/P01.01-cluster-netpol`, one commit each for P01.01a to P01.01c. Status record:
  `in_review`.
- Done: `scripts/cluster_up.sh` (kind 0.33.0, Kubernetes 1.36.4, Calico 3.33.1), UI-to-API-only egress rule,
  rewritten `scripts/netpol_test.sh`. The Phase 0 egress policies needed no change.
- Evidence: [apply](../evidence/phase1/netpol-apply.txt), [test and negative controls](../evidence/phase1/netpol-test.txt).
- Not shown: real M5 or UI workloads (test pods stand in for them; NET-003 stays with its task), ingress rules,
  and a run from an empty Docker cache on a second machine. `shellcheck` was not available.
- For P01.04: label pods `app: <module>` (`ui`, `gateway`, `tools` matter to the policies). The cluster maps no host
  ports; add `extraPortMappings` in `cluster_up.sh` and recreate the cluster if Ingress needs them. A job that
  downloads from the internet (model import) is blocked unless it goes through M5.
- This PC: Docker Desktop was started by this session; containers of another project restarted with it and were left
  alone. The cluster is still running and the current kubectl context is `kind-idea-validator` (it was `minikube`).
  Free host memory was as low as 0.8 GB.
- Next: P01.03 (gateway and UI), only after P01.02 is merged into `dev` and the primary session says so.
- Messages: primary session message received 2026-11-28 (registry on `dev` stays; order after P01.01 is P01.03).

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
