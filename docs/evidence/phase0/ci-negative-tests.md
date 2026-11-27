# GitHub negative tests and gate behaviour (2026-11-28)

| Case | Pull request | Expected | Observed |
|---|---|---|---|
| Promotion without approval | [#8](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8) `dev → main` | blocked | 21/21 checks success, `mergeStateStatus=BLOCKED`, `reviewDecision=REVIEW_REQUIRED` |
| Wrong head into main | [#9](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/9) `chore/phase-0-bootstrap → main` | policy check fails, blocked | `branch-policy` FAILURE and `ci-gate` FAILURE ([run](https://github.com/Abdullah-SE-bit/SCD_Proj/actions/runs/46063792835)); `BLOCKED`; closed without merge |

In #9 the required review was also missing, so the block had two causes; the two failed checks are the
evidence for the policy.

## Protection re-read after the merges
```
main checks=21 strict=false reviews=1 admins=true force=false delete=false
dev  checks=21 strict=true  reviews=0 admins=true force=false delete=false
```
