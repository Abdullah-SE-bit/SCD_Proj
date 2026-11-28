---
name: scd-task-workflow
description: SCD project rules for task-execution, phase-gate, handoff-management, ai-usage-log. Use when starting, resuming or finishing any project task.
---

# scd-task-workflow

**Purpose:** project-specific rules for task-execution, phase-gate, handoff-management, ai-usage-log. Generic skills may help, but never override these.
**Use when:** starting, resuming or finishing any project task.
**Read first:** docs/planning/ImplementationPlan.md, docs/planning/DefinitionOfDone.md, your handoff file.
**Requirements:** GIT-002, GIT-003, DOC-001.

## Workflow
1. `python harness/verification/scd.py identity`
2. `git fetch origin`; read Mandoff.md, your handoff and open issues
3. Pick a task you own whose dependencies are done; `python harness/verification/scd.py claim <ID>`
4. Branch `type/<ID>-name` from `origin/dev`
5. Work only inside the task's file scope
6. Run the task's verification commands
7. Update AI-usage log, handoff, docs; add the status file as done with evidence
8. Open the PR with `python harness/verification/scd.py gh -- pr create --base dev`
9. Merge into dev once checks pass, then tell the other session (see scd-session)

**Tools:** git, scd.py, gh through scd.py.
**Restrictions:** no unclaimed or blocked tasks; no phase gate marked done by hand without evidence. No secrets in files or messages.
**Verify:** `python harness/verification/scd.py check task-policy`.
**Outputs:** PR, status file, handoff entry.
**On failure:** claim rejected or dependency unmet: record BLOCKED and choose another task.
**Complete when:** Definition of done satisfied and PR merged.
