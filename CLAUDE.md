# Working rules

Two Claude Code sessions work on this repository in parallel, each in its own clone.

## Ownership

| Contributor | Clone folder | Owns | Branch prefix |
|---|---|---|---|
| `Abdullah-SE-bit` | `SCD_Proj` | `backend/` | `backend/` |
| `Demidoga` | `SCD_Proj_demidoga` | `frontend/` | `frontend/` |

The clone folder you are in decides which contributor you work for. Edit only what that contributor owns.

## Git

- After the foundation commit, do not commit to `main` directly. Use a small branch and a pull request, reviewed by the other contributor.
- Pull `main` before starting a branch.
- Each clone has its own `user.name` and `user.email`. Do not change them.
- Do not run `gh auth switch`; the active `gh` account is shared by both sessions.
- To open or review a pull request as `Demidoga` (PowerShell, one line):
  `$env:GH_TOKEN = gh auth token --user Demidoga; gh pr create; Remove-Item Env:GH_TOKEN`
- Never commit secrets or `.env` files.

## Shared files

Changes to the API contract, `README.md`, `CLAUDE.md` or `.gitignore` go in their own pull request, and the other session is told about them.
