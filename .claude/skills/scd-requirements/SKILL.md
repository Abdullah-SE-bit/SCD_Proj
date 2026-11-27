---
name: scd-requirements
description: SCD project rules for scd-requirements, architecture-compliance. Use when interpreting a requirement, designing a module, or changing status or traceability.
---

# scd-requirements

**Purpose:** project-specific rules for scd-requirements, architecture-compliance. Generic skills may help, but never override these.
**Use when:** interpreting a requirement, designing a module, or changing status or traceability.
**Read first:** docs/requirements/, docs/architecture/, docs/source/.
**Requirements:** all.

## Workflow
1. Find the requirement IDs in the registry
2. Check the PDF page it cites
3. Check Ambiguities for open interpretations
4. Verify module boundaries against Architecture
5. Update status and evidence only; run `python harness/verification/scd.py render`

**Tools:** Read, pdf skill.
**Restrictions:** never reword or delete a requirement (protected); never mark verified without evidence. No secrets in files or messages.
**Verify:** `python harness/verification/scd.py check requirements-registry` and `traceability`.
**Outputs:** traceable change.
**On failure:** conflict between sources: add to Ambiguities and PendingDecisions, ask.
**Complete when:** checks pass and the other contributor reviewed.
