# Known limitations (Phase 0)

1. Application: nothing is implemented.
2. Course PDFs are not in the public repository (D-01); a fresh clone needs them copied in.
3. Assignment 1, referenced by M2, was not supplied.
4. The independent review was AI-assisted; no human has audited the requirements line by line. Both accounts'
   sessions run on one PC, so who gave each decision cannot be established from the repository.
5. NetworkPolicy manifests are schema-valid but enforcement is untested; no cluster was created.
6. Jenkinsfile syntax and execution are unverified; delivery scripts were tested only with a fake `kubectl`.
7. docker-compose.yml is an explicit empty placeholder.
8. Hooks are text-pattern guard rails: interpreters can write files, variable-built subcommands can avoid the
   prompt, and bypass-permissions mode may skip prompts. Both tokens share one OS user (PermissionPolicy).
9. The authorization label stays on a pull request when new commits are pushed.
10. Rollback does not restore ConfigMaps or replica counts.
11. `dev` has no review (A-06); mutual review (COL-002) happens only on promotions, so both members must author
    and review them. Sessions merge into `dev` without asking.
12. The repository is public; commit email addresses and their hashes are visible.
13. Roll numbers, signatures, annotations and credentials are outstanding.
14. Security-guidance commit review and Serena analysis are unverified.

Open low review findings: [ReviewResponses](ReviewResponses.md).
