---
name: scd-frontend
description: SCD project rules for frontend-engineering. Use when building or reviewing UI.
---

# scd-frontend

**Purpose:** project-specific rules for frontend-engineering. Generic skills may help, but never override these.
**Use when:** building or reviewing UI.
**Read first:** docs/architecture/MVP.md screens.
**Requirements:** USR-003, USR-006, USR-010, M01-*.

## Workflow
1. Use the frontend-design skill for visual choices
2. Handle loading, empty, error, approval and abstention states
3. Accessible labels and keyboard use
4. API address from runtime config
5. Component tests per state

**Tools:** Vitest, Playwright, frontend-design.
**Restrictions:** no direct model or scout calls; no hard-coded localhost; no verdict logic in UI. No secrets in files or messages.
**Verify:** `npm --prefix services/ui test`.
**Outputs:** components, tests, screenshots.
**On failure:** missing API: use contract fixtures labelled as fixtures.
**Complete when:** states tested and shown.
