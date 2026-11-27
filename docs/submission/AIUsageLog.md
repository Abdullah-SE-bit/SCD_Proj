# AI-usage log

Columns required by Guide 11.2. Record what really happened; humans fill "What you changed" after reviewing.

| Date | Tool | What you asked for | What you changed | Why |
|---|---|---|---|---|
| 2026-11-27 | Claude Code | Install plugins, MCP servers and language servers on this PC | none | tooling setup |
| 2026-11-27 | Claude Code | Add collaborator, two clones with separate identities, foundation commit `26b5642` | none | repository setup; text written by AI |
| 2026-11-28 | Claude Code | Phase 0: requirements, architecture, plan, harness, CI, documents (this foundation) | pending human review | all content AI-generated from the two course PDFs and the Phase 0 instruction |
| 2026-11-28 | Claude Code | After the owner enabled maintenance mode: fix four harness defects, run CI, open pull requests, record negative tests | owner enabled maintenance mode; content unchanged by humans | harness identity check blocked all commits |
| 2026-11-28 | Claude Code | Fix review findings H1-H4, H6 and M8 (harness bypasses) with tests | owner chose to fix High and Medium findings and authorised protected edits; no edits by humans | independent review of PR 8 |

Human decisions so far: see `docs/requirements/ApprovedDecisions.md`.
