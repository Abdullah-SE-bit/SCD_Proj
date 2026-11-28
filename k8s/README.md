# Kubernetes manifests

Status: the whole skeleton deploys with `sh scripts/deploy.sh`; `sh scripts/smoke_test.sh` probes it.
Requests and limits are provisional until measured (P10.01).
See [DeploymentArchitecture](../docs/architecture/DeploymentArchitecture.md).

| File | Holds |
|---|---|
| `namespace.yaml`, `networkpolicy.yaml` | namespace and network rules |
| `config.yaml` | non-secret settings |
| `data.yaml` | Postgres and Qdrant with volume claims, Redis |
| `apps.yaml` | one Deployment and Service per module, rolling update with `maxUnavailable: 0` |
| `jobs.yaml` | ingestion CronJob |
| `ingress.yaml`, `ingress-controller.yaml` | single entry point (Traefik) |

Secrets are never in these files: `deploy.sh` generates `db-secret`; `load_secrets.sh` creates `api-keys` from
`.env`. Undo a rollout with `kubectl -n idea-validator rollout undo deploy/<name>`.

## Cluster
Needs Docker, kind 0.33.0 and kubectl. On Windows run the scripts from Git Bash.

```sh
sh scripts/cluster_up.sh
```

Creates the one-node kind cluster `idea-validator` (Kubernetes 1.36.4) with Calico 3.33.1 and switches the kubectl
context to `kind-idea-validator`. The node image is pinned by digest and the Calico manifest by checksum.
Delete it with `kind delete cluster --name idea-validator`.

## Network policies
Applied by `deploy.sh`. To test them:

```sh
sh scripts/netpol_test.sh
```

| Policy | Pods | Allows egress to |
|---|---|---|
| `default-deny-egress` | all | nothing |
| `allow-dns` | all | UDP and TCP 53 on `kube-dns` |
| `allow-within-namespace` | all except `app: ui` | any pod in `idea-validator` |
| `allow-ui-to-api` | `app: ui` | `app: gateway` pods only |
| `allow-tools-internet` | `app: tools` (M5) | TCP 80 and 443 on public addresses |

Policies select pods by the `app` label, so every workload must set it to its module directory name
(`tools`, `gateway`, `ui`, ...). A pod that needs the internet but is not `app: tools` is blocked by design.
There are no ingress rules: any pod in the namespace except the UI can reach any other.
