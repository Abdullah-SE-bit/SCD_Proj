# Kubernetes manifests

Status: **scaffold**. Only the namespace and egress NetworkPolicies exist; no workload is deployed.
Enforcement is **unverified** until task P01.01 runs `scripts/netpol_test.sh` on a cluster with Calico.
The UI-reaches-API-only ingress rule (Guide Figure 3) is added with the workloads in P01.01.
See [DeploymentArchitecture](../docs/architecture/DeploymentArchitecture.md).

## Cluster
Needs Docker, kind 0.33.0 and kubectl. On Windows run from Git Bash.

```sh
sh scripts/cluster_up.sh
```

Creates the one-node kind cluster `idea-validator` (Kubernetes 1.36.4) with Calico 3.33.1 and switches the kubectl
context to `kind-idea-validator`. The node image is pinned by digest and the Calico manifest by checksum.
Delete it with `kind delete cluster --name idea-validator`.

## Network policies

```sh
kubectl apply -k k8s
```

| Policy | Pods | Allows |
|---|---|---|
| `default-deny-egress` | all | nothing |
| `allow-dns` | all | UDP and TCP 53 to `kube-dns` |
| `allow-within-namespace` | all | any pod in `idea-validator` |
| `allow-tools-internet` | `app: tools` (M5) | TCP 80 and 443 to public addresses |

Policies select pods by the `app` label, so every workload must set it to its module directory name
(`tools`, `gateway`, `ui`, ...). A pod that needs the internet but is not `app: tools` is blocked by design.
