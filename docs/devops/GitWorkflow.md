# Git workflow

`task branch → dev → main`.

1. One issue per task. `python harness/verification/scd.py claim P01.01`.
2. `git switch -c feat/P01.01-short-name origin/dev`. Types: feat, fix, chore, docs, test, ci, refactor.
3. Conventional commits (`feat(verdict): add duplicate gate`). No filler commits.
4. PR into `dev` with the template. **No review.** When GitHub allows the merge (no conflicts, required checks
   green), merge it with a merge commit. Never request changes on a pull request that can merge without conflicts;
   post findings as a comment. Squash and rebase are disabled so both authors' history survives.
5. After merge delete the task branch and release the claim (a human deletes `claim/<ID>`; hooks forbid it).
6. Promotion: PR `dev → main`; the other collaborator reviews and approves; merge after green checks.
7. `main` does not require up-to-date branches, to avoid a permanent sync loop. If GitHub reports
   `main` and `dev` diverged in content, open `main → dev`.

## Deliberate merge conflict (GIT-004, task P10.02)
Planned: two branches from the same `dev` commit edit the same lines of a document; merge one, resolve the
other in its PR, capture screenshots of the conflict and the resolution.

## Identities
Each clone has local `user.name`, `user.email` and a credential helper pinned to its GitHub login. Run `gh`
through `python harness/verification/scd.py gh -- ...`; never `gh auth switch`. Check with
`python harness/verification/scd.py identity`.

History note: commit `26b5642` was pushed to `main` before protection existed (repository bootstrap).
