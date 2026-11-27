---
name: scd-verdict-engine
description: SCD project rules for verdict-engine. Use when working on M11, rubric constants or verdict config.
---

# scd-verdict-engine

**Purpose:** project-specific rules for verdict-engine. Generic skills may help, but never override these.
**Use when:** working on M11, rubric constants or verdict config.
**Read first:** docs/architecture/VerdictEngineSpecification.md, config/verdict.defaults.json.
**Requirements:** M11-*, GAT-*, SCR-*, FLW-001.

## Workflow
1. Confirm decision D-07
2. Write edge tests from the specification list first (TDD)
3. Implement pure functions
4. Reproduce the worked example
5. Load config from file or ConfigMap

**Tools:** pytest.
**Restrictions:** no network, model, clock or randomness; read AMB-24 before asserting flip counts. No secrets in files or messages.
**Verify:** `pytest services/verdict -q`.
**Outputs:** engine, tests.
**On failure:** source ambiguity: ask, do not choose silently.
**Complete when:** every listed test passes.
