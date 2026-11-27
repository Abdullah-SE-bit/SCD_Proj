# Agent harness

| Layer | Where | Enforces |
|---|---|---|
| GitHub protection | server | no direct or force pushes, checks, review on main (strongest) |
| CI | `.github/workflows/pr-checks.yml` + `scd.py` | targets, task scope, dependencies, owner, handoff, AI log, protected files, secrets, contracts, Phase 0 scope |
| Claude hooks | `.claude/settings.json` → `guard.py` → `scd.py` | early denial of the same mistakes locally; asks a human for approvals and merges |
| Permissions | `.claude/settings.json` | deny reading `.env`, account switching, force push |
| Instructions | CLAUDE.md, rules, skills | process |

Commands: `python harness/verification/scd.py identity | claim <ID> | check <name> | all | render | gh -- <args>`.

Hooks: `PreToolUse` (Bash, PowerShell, file edits) returns deny or ask; `SessionStart` reports identity and
branch; `Stop` warns when work is uncommitted and the handoff is untouched. A crashing pre-tool hook blocks the
tool (exit 2). Claude Code asks to trust new project hooks; each clone's user must accept them.

Claims: `claim` creates `claim/<ID>` on GitHub atomically; a second claim is rejected by git.
