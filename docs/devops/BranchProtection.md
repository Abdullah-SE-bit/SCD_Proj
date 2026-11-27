# Branch protection

Applied through the GitHub API on 2026-11-28 and read back. Evidence: `docs/evidence/phase0/github-protection.md`.

| Rule | main | dev |
|---|---|---|
| Pull request required | yes | yes |
| Approving reviews | 1 | 0 (D-11) |
| Dismiss stale approvals | yes | yes |
| Required checks (21, GitHub Actions app only) | yes | yes |
| Branch up to date | no | yes |
| Conversations resolved | yes | yes |
| Applies to administrators | yes | yes |
| Force push / deletion | blocked | blocked |
| Merge method | merge commit only (repository setting) | same |

**Rule from 2026-11-28 (decision A-06):** review only into `main`. For `dev` the intended settings are: pull
request and 21 required checks, no approval, no conversation resolution, no up-to-date requirement. The table
above records what was applied first; the owner changes `dev` on GitHub, and sessions cannot.

Limits: a repository administrator can still change these settings; user-owned repositories cannot restrict who
merges; the required approval can come from any account with write access other than the author, here only the
other collaborator. `require_last_push_approval` is off because with two people it can deadlock promotion.
