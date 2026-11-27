---
name: scd-fine-tuning
description: SCD project rules for fine-tuning, human-annotation. Use when building datasets, training, serving or comparing the scoring model.
---

# scd-fine-tuning

**Purpose:** project-specific rules for fine-tuning, human-annotation. Generic skills may help, but never override these.
**Use when:** building datasets, training, serving or comparing the scoring model.
**Read first:** HumanAnnotationPlan, EvaluationStrategy.
**Requirements:** FT-*, M10-*, TUN-001, TUN-002.

## Workflow
1. Generate drafts with the hosted model
2. Hand the checking to students; record checked_by
3. Split by idea; exclude labelled verdict ideas; test for leakage
4. Train on free GPU; record settings and loss
5. Merge, quantise, publish outside git
6. Compare three models on the checked set

**Tools:** Unsloth, TRL, pytest.
**Restrictions:** never write or alter a human label; never report unmeasured metrics. No secrets in files or messages.
**Verify:** leakage and format tests.
**Outputs:** dataset, settings, comparison table.
**On failure:** no GPU or labels: report blocked.
**Complete when:** all FT requirements evidenced.
