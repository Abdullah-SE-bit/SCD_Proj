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

Optional `accepted_objections` (`dimension`, `reason`): each costs 0.5 score (at most 1.0) and 0.1 confidence; the
answer lists `adjustments`. `stability` is BORDERLINE when any of the 14 sensitivity runs changes the verdict, and
`flips` lists those runs. `what_would_make_go` suggests the smallest change.

`POST /whatif` takes the same body plus `changes` (`scores`: new values by dimension; `profile`: new values) and
answers with `hypothetical: true`.

The worked example of Description 5.4 gives 4 flipping runs of 14, not the 3 shown there: its own rules also move
competition by one point (AMB-24, ask the instructor).

Run from this directory: `python -m scd_verdict.app`. Tests: `pytest services/verdict`.
