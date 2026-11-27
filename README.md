# SCD_Proj: Idea Generator with Go / No-Go

Course project (CS4032 Software Construction and Development). **Status: Phase 0, foundation only. There is no
application to run yet.**

| Start here | |
|---|---|
| What must be built | [requirements](docs/requirements/Requirements.md), [MVP](docs/architecture/MVP.md) |
| How | [architecture](docs/architecture/Architecture.md), [plan](docs/planning/ImplementationPlan.md) |
| Decisions needed | [pending decisions](docs/requirements/PendingDecisions.md) |
| Working rules | [CLAUDE.md](CLAUDE.md), [contributing](CONTRIBUTING.md) |
| Current state | [Mandoff](Mandoff.md), [Phase 0 report](docs/handoff/Phase0VerificationReport.md) |
| All documents | [docs index](docs/README.md) |

## Check the foundation
```bash
uv run --no-project --python 3.12 --with-requirements requirements-dev.txt python harness/verification/scd.py all
```
Needs `kubeconform` on PATH. Setup: [EnvironmentSetup](docs/environment/EnvironmentSetup.md).

## Layout
`services/` modules · `jobs/` offline jobs · `contracts/` schemas · `config/`, `rubrics/`, `eval/` · `k8s/` ·
`harness/` development enforcement · `docs/`.
