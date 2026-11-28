# Known limitations (Phase 0)

1. Application: service skeletons with probes and a UI-to-gateway path serving a fixture verdict. Nothing is
   evaluated.
2. Course PDFs are not in the public repository (D-01); a fresh clone needs them copied in.
3. Assignment 1, referenced by M2, was not supplied.
4. The independent review was AI-assisted; no human has audited the requirements line by line. Both accounts'
   sessions run on one PC, so who gave each decision cannot be established from the repository.
5. NetworkPolicy enforcement is tested with test pods only (P01.01); no workload is deployed. There are no
   ingress rules, so any pod in the namespace except the UI can reach any other.
6. Jenkins ran on the local cluster (P01.05). It has no accounts and runs as root with the Docker socket; the
   nightly evaluation stage fails until P08.02; the GHCR push path is untested.
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

Rubrics (P03.03): student review is open and CI does not run their test.

Open low review findings: [ReviewResponses](ReviewResponses.md).

## Found at the P01 gate
- After `scripts/jenkins_up.sh` recreates the job, Jenkins does not poll until one build is started by hand.
- `CLAUDE.md` still says a `done` record needs a label; decision A-08 removes it.
- The registry `scd-registry` must run for cluster pods to pull Jenkins-built images again.
