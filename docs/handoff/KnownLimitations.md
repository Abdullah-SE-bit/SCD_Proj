# Known limitations (Phase 0)

1. Application: nothing is implemented.
2. Course PDFs are not in the public repository (D-01); a fresh clone needs them copied in.
3. Assignment 1, referenced by M2, was not supplied.
4. Requirements extraction is not yet independently audited (P00.06).
5. NetworkPolicy manifests are schema-valid but enforcement is untested; no cluster was created.
6. Jenkinsfile has never run on a Jenkins server (see the verification report for syntax validation).
7. docker-compose.yml is an explicit empty placeholder.
8. Hooks are text-pattern guard rails; both tokens share one OS user (PermissionPolicy).
9. Hooks of this harness load in new sessions after each user trusts them; verified by running the hook program,
   not yet inside a fresh interactive session.
10. `dev` needs no approval (D-11).
11. The repository is public; commit email addresses are visible.
12. Roll numbers, signatures, annotations and credentials are outstanding.
13. Security-guidance commit review and Serena analysis are unverified.
