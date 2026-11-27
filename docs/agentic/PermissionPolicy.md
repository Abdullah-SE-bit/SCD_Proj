# Permission policy and trust limits

Automatic and human-only actions: [HumanInterventionPolicy](../planning/HumanInterventionPolicy.md).

Protected files are listed in `harness/policies/project.json`. A human starts Claude with
`SCD_HARNESS_MAINTENANCE=1` to edit them locally and adds the `authorized-protected-change` label to the PR.

**Limits, stated plainly**
- Hooks match command text. A determined or confused agent can evade a pattern (for example a script that runs
  git). They are guard rails, not a security boundary.
- Both GitHub tokens are in one Windows user's keyring. Either session could technically act as either account.
  Isolation is procedural. Real isolation needs separate OS users or machines.
- The primary account is repository admin and could change protection.
- The label and the environment variable can be set by anyone with those accounts.
- The CI workflow file is taken from the PR; only human review on main catches a weakened workflow.
- Never run Claude with administrator rights or in bypass-permissions mode on this repository.
