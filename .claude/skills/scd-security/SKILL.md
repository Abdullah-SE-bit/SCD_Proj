---
name: scd-security
description: SCD project rules for security-audit. Use when reviewing input handling, egress, secrets, dependencies or injection defence.
---

# scd-security

**Purpose:** project-specific rules for security-audit. Generic skills may help, but never override these.
**Use when:** reviewing input handling, egress, secrets, dependencies or injection defence.
**Read first:** SecurityArchitecture.
**Requirements:** SEC-*, M05-002, M12-*, ETH-005.

## Workflow
1. Map the change to the threat table
2. Add a failing security test first
3. Run secret scan and dependency checks
4. Use claude-security for deep audits when asked

**Tools:** gitleaks, bandit, pip-audit.
**Restrictions:** no real secrets in tests; report instead of exploiting. No secrets in files or messages.
**Verify:** `python harness/verification/scd.py check secret-scan` and `dependency-security`.
**Outputs:** findings with file and line.
**On failure:** secret found: stop, tell the user to rotate it.
**Complete when:** no unresolved high finding.
