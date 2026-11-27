---
name: scd-evaluation
description: SCD project rules for evaluation-engineering, evidence-collection. Use when running evaluations or collecting screenshots and logs.
---

# scd-evaluation

**Purpose:** project-specific rules for evaluation-engineering, evidence-collection. Generic skills may help, but never override these.
**Use when:** running evaluations or collecting screenshots and logs.
**Read first:** EvaluationStrategy, ScreenshotChecklist.
**Requirements:** OPS-005, FT-009, TUN-*, SUB-005..008.

## Workflow
1. Run the real command
2. Store raw output with date, commit and command
3. Summarise without rounding away failures
4. Link evidence from requirement or task

**Tools:** pytest, playwright.
**Restrictions:** never fabricate, stage or reuse stale evidence. No secrets in files or messages.
**Verify:** evidence files exist and cite a commit.
**Outputs:** results JSON, screenshots.
**On failure:** run fails: record the failure.
**Complete when:** evidence linked.
