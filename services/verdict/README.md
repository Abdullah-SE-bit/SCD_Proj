# services/verdict (M11)

Deterministic verdict engine: gates, weighted score, confidence, thresholds, floor and abstention. No model, network,
clock or randomness. Specification: `docs/architecture/VerdictEngineSpecification.md`.

`POST /verdict` takes `scores` (at most six records; an abstaining scorer sends none), `profile`, `config`
(overrides per section, `{}` for the deployed rules) and `evidence` (the cited evidence items). Optional: `idea_id`,
`version`, `run_id`.

Facts the gates read from the scores' `features`: `feasibility.effort_hours`, `risk.blocker`,
`differentiation.duplicate_product`. Without an effort estimate, a risk score or a differentiation score the answer is
`INSUFFICIENT_EVIDENCE`. Extra answer fields: `reasons`, `gate_reasons`, `abstained`.

Rules come from the file named by `VERDICT_CONFIG` (ConfigMap `verdict-config` on the cluster).

Not yet: sensitivity, challenge and what-if (P03.02). Until then `sensitivity.runs` is 0 and `stability` is not tested.

Run from this directory: `python -m scd_verdict.app`. Tests: `pytest services/verdict`.
