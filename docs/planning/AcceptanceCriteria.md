# Acceptance criteria

- Per requirement: the `acceptance` and `verification` columns in
  [Requirements](../requirements/Requirements.md).
- Per task: the Acceptance line in [ImplementationPlan](ImplementationPlan.md).
- Per phase: the gate's demonstrable result, all its tasks done on `dev`, all required checks green, and the
  demonstration evidence stored under `docs/evidence/`.

A requirement moves to `implemented` when code and tests merge, and to `verified` only with evidence from the
stated verification method. Documentation alone never changes a status.
