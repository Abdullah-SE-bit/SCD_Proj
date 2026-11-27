---
name: scd-review
description: SCD project rules for independent-review. Use when reviewing the other contributor's pull request.
---

# scd-review

**Purpose:** project-specific rules for independent-review. Generic skills may help, but never override these.
**Use when:** reviewing the other contributor's pull request.
**Read first:** docs/agentic/CrossSessionProtocol.md, PR template.
**Requirements:** COL-002.

## Workflow
1. `python harness/verification/scd.py identity` (must not be the author)
2. Fetch and read the full diff
3. Compare against requirements and the source PDFs
4. Run verification commands
5. Post findings as a comment review
6. Present findings to your account owner; submit approve or request-changes only on their decision, stating Claude assisted

**Tools:** git, scd.py gh, code-review skill.
**Restrictions:** never approve your own work; never submit an approval the human did not give. No secrets in files or messages.
**Verify:** commands run and quoted.
**Outputs:** review with severity-ranked findings.
**On failure:** cannot verify something: say so.
**Complete when:** owner decided and review submitted.
