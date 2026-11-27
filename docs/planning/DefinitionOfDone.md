# Definition of done

A task is done when all are true:
1. Acceptance criteria met and demonstrated by the listed commands.
2. Required tests exist and pass in CI.
3. Contracts, documentation and decision records updated.
4. Handoff file and AI-usage log updated.
5. Evidence stored or linked.
6. PR into `dev` reviewed by the other contributor and merged with all checks green.
7. `harness/task-registry/status/<ID>.json` added in that PR (`status`, `pr`, `evidence`).

A phase gate additionally needs every member task done and the phase demonstration run on the cluster (from
Phase 1). Phase 0 is done only after the promotion PR is merged into `main` with genuine collaborator approval.
