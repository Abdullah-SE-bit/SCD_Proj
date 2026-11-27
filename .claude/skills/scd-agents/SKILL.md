---
name: scd-agents
description: SCD project rules for agent-workflows, agenticops. Use when working on M3, M8, M9, M12 or M13.
---

# scd-agents

**Purpose:** project-specific rules for agent-workflows, agenticops. Generic skills may help, but never override these.
**Use when:** working on M3, M8, M9, M12 or M13.
**Read first:** docs/architecture/AgentWorkflows.md.
**Requirements:** M03-*, M08-*, M12-*, M13-*, OPS-*.

## Workflow
1. Write the state machine transitions as tests first
2. Bound retries, timeouts, rounds and budgets
3. Require evidence ids; otherwise abstain
4. Trace every step with run_id
5. Record responses once and replay in tests

**Tools:** pytest.
**Restrictions:** no live model in CI; no model decides a verdict. No secrets in files or messages.
**Verify:** behaviour tests.
**Outputs:** tested transitions, traces.
**On failure:** invalid model output: retry once, fall back, log.
**Complete when:** four behaviour cases pass.
