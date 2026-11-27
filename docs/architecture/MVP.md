# MVP specification

Status: proposed. Nothing described here is implemented.

## Purpose and user
Help a student choose a project: propose ideas (Discover) or judge one (Validate) with evidence, a rule-based
verdict, what would change it and how stable it is. Decision support, not a success prediction. The user is a
student with a profile (skills, hours, weeks, team, compute, goal, interests).

## Journeys
| # | Journey | Requirements |
|---|---|---|
| J1 | Register, log in, save and edit a profile; later recommendations change | USR-001 |
| J2 | Discover: ask in a niche or generally; watch agents, tool calls and spend; get ranked ideas with verdicts and reasons | USR-002, USR-003 |
| J3 | Validate: submit idea; answer only result-changing questions; approve or decline an expensive search; read the card | USR-004, USR-005, USR-006 |
| J4 | Ask what would make it GO; apply one change; get version 2 | USR-007 |
| J5 | Challenge a claim; it is defended or removed | USR-008 |
| J6 | History, versions, compare two ideas on six dimensions | USR-009 |
| J7 | Understand INSUFFICIENT EVIDENCE | USR-010 |

## Screens
| Screen | Contents | States |
|---|---|---|
| Sign in / register | email, password | invalid, rate limited |
| Profile | all profile fields | unsaved, saved |
| Chat / start | Discover or Validate, niche wish or idea text | clarifying question |
| Live run | running agent, tool calls, spend, approval prompt | waiting approval, failed step, retried |
| Verdict card | verdict, stability, 4 gates, 6 scores with evidence links, weights, thresholds, confidence, flips, what-would-make-GO, challenge buttons | GO, PIVOT, NO-GO, INSUFFICIENT EVIDENCE (what is missing) |
| Discover results | ranked ideas, verdict and short reason | none survived |
| History and compare | ideas, versions, two-column comparison | empty |
| Dashboard | cost per verdict, latency per agent, cache hits, fallbacks, approvals, blocked injections | no data |

## Three levels
1. **Walking skeleton (Phase 1):** every module container deployed; browser to fixture verdict card, labelled
   `FIXTURE DATA`; Jenkins deploys it; NetworkPolicy enforced.
2. **Academically compliant MVP (Phases 2-10):** every mandatory requirement in the registry (234). Nothing in
   it may be dropped to simplify work.
3. **Optional (only after 2):** extra sources, Grafana, tunnel webhooks, Helm, richer niche visualisation.

## Boundaries
In scope: public idea data, the 14 modules, evaluation and submission evidence. Out: predicting success,
private data, logins to source sites, mobile apps, payments, production hosting.

## Acceptance and demonstration
Acceptance is per requirement ([Requirements](../requirements/Requirements.md)) and per phase gate
([ImplementationPlan](../planning/ImplementationPlan.md)). Final demonstration: register; set a portfolio
profile; Discover in a niche; open a card; challenge a claim; apply a what-if to get version 2; validate a thin
idea to show INSUFFICIENT EVIDENCE; change the profile and show a different verdict; show trace, dashboard,
drift report, pods, rollout, rollback and the NetworkPolicy test.
