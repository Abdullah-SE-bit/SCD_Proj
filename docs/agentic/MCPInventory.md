# MCP server inventory

Checked 2026-11-28 with `claude mcp list`. All user scope; `.mcp.json` is intentionally empty to avoid
duplicate project definitions.

| Server | State | Class |
|---|---|---|
| context7 | connected; query verified 2026-11-27 | primary |
| playwright | connected; page load verified 2026-11-27 | primary |
| chrome-devtools | connected | recommended |
| serena 2.1.0 | connected; code analysis untested (no code) | recommended |
| Claude Docs, claude-design | connected | not used by this project |
| GitHub MCP | not enabled | unnecessary: `gh` |
| PostgreSQL, Redis, Docker, Kubernetes, Jenkins, Grafana | not installed | unnecessary: native CLIs |
| Hugging Face, Slack, Figma | not installed | optional, later |
| filesystem, memory, fetch, search | not installed | built in |

Third-party servers run through `npx ...@latest` (playwright, chrome-devtools): unpinned. Pin versions before
relying on them for evidence.
