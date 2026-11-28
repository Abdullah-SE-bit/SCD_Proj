# Definition of done

A task is done when all are true:
1. Acceptance criteria met and demonstrated by the listed commands.
2. Required tests exist and pass in CI.
3. Contracts, documentation and decision records updated.
4. Handoff file and AI-usage log updated.
5. Evidence stored or linked.
6. PR into `dev` merged with all checks green. No review is required for `dev` (decision A-06).
7. `harness/task-registry/status/<ID>.json` added in that PR (`status: done`, `pr`, `evidence`). A pull request
   that records `done` needs the owner's `authorized-protected-change` label.

A phase gate additionally needs every member task done and the phase demonstration run on the cluster (from
Phase 1). One gate PR may record its member tasks and the gate together. Phase 0 is done only after the
promotion PR into `main` is merged with the other collaborator's approval.
