---
name: scd-release
description: SCD project rules for release-verification, academic-documentation, viva-preparation. Use when phase gates, report, submission and viva study.
---

# scd-release

**Purpose:** project-specific rules for release-verification, academic-documentation, viva-preparation. Generic skills may help, but never override these.
**Use when:** phase gates, report, submission and viva study.
**Read first:** SubmissionChecklist, ReportOutline.
**Requirements:** SUB-*, DDR-001, LOG-*, COL-003.

## Workflow
1. Run all checks
2. Walk the checklist row by row with evidence
3. Draft the report from measured results
4. Prepare per-module explanations and likely questions for both students

**Tools:** pdf skill.
**Restrictions:** students sign; never fill signatures, hours or roll numbers. No secrets in files or messages.
**Verify:** `python harness/verification/scd.py all`.
**Outputs:** checklist, report draft, viva notes.
**On failure:** missing evidence: list it as missing.
**Complete when:** students confirm.
