# Definition of done

A task is done when all are true:
1. Acceptance criteria met and demonstrated by the listed commands.
2. Required tests exist and pass in CI.
3. Contracts, documentation and decision records updated.
4. Handoff file and AI-usage log updated.
5. Evidence stored or linked.
6. PR into `dev` reviewed by the other contributor and merged with all checks green.
7. `harness/task-registry/status/<ID>.json` records it (`status`, `pr`, `evidence`).

## Status values
| Status | Meaning | Who sets it |
|---|---|---|
| `in_review` | merged work awaiting the other contributor's review; unblocks only tasks of the same phase | the task owner's pull request |
| `done` | reviewed; needs `reviewed_by` (not the owner) and a `review` link | a phase gate pull request carrying the human's `authorized-protected-change` label |

A gate and any later phase need `done`. Work recorded `done` before review must be returned to `in_review`.

A phase gate additionally needs every member task done and the phase demonstration run on the cluster (from
Phase 1). Phase 0 is done only after the promotion PR is merged into `main` with genuine collaborator approval.
