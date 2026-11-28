# SCD_Proj: Idea Generator with Go / No-Go

Course project (CS4032 Software Construction and Development). **Status: Phase 1, walking skeleton.** Every module
runs on the cluster, but only answers health checks; the one visible feature is a fixed verdict card marked
`FIXTURE DATA`. Nothing is evaluated yet.

| Start here | |
|---|---|
| What must be built | [requirements](docs/requirements/Requirements.md), [MVP](docs/architecture/MVP.md) |
| How | [architecture](docs/architecture/Architecture.md), [plan](docs/planning/ImplementationPlan.md) |
| Decisions needed | [pending decisions](docs/requirements/PendingDecisions.md) |
| Working rules | [CLAUDE.md](CLAUDE.md), [contributing](CONTRIBUTING.md) |
| Current state | [Mandoff](Mandoff.md), handoff files in `docs/handoff/` |
| All documents | [docs index](docs/README.md) |

## Start it on Kubernetes
Needs Docker (about 8 GB of memory), kind 0.33.0, kubectl, curl and git. Run from Git Bash on Windows.

```sh
sh scripts/cluster_up.sh      # kind cluster "idea-validator" with Calico
sh scripts/deploy.sh          # build, load and apply everything; generates the database password
sh scripts/smoke_test.sh      # probes every service and the path through the ingress
kubectl -n ingress port-forward svc/traefik 8080:80
```

Then open <http://localhost:8080>. API keys are only needed once the data modules exist: put them in `.env` (names in
`.env.example`) and run `sh scripts/load_secrets.sh`.

Check the network rules: `sh scripts/netpol_test.sh`. Remove everything: `kind delete cluster --name idea-validator`.

## Develop without the cluster
```sh
cp .env.example .env                               # then set POSTGRES_PASSWORD
docker compose up -d                               # Postgres (port 55432), Redis (6379), Qdrant (6333)
docker compose --profile app up -d --build         # also the gateway (port 8000) and UI (port 8081)
```
One service: `cd services/<name>` then `python -m scd_<name>.app`.

## Check the repository
```sh
uv run --no-project --python 3.12 --with-requirements requirements-dev.txt python harness/verification/scd.py all
```
Needs `kubeconform` on PATH. Setup: [EnvironmentSetup](docs/environment/EnvironmentSetup.md).

## Layout
`services/` modules · `jobs/` offline jobs · `contracts/` schemas · `config/`, `rubrics/`, `eval/` · `k8s/` ·
`scripts/` cluster and checks · `harness/` development enforcement · `docs/`.
