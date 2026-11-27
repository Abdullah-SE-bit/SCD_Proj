# Kubernetes manifests

Status: **scaffold**. Only the namespace and egress NetworkPolicies exist; no workload is deployed.
Enforcement is **unverified** until task P01.01 runs `scripts/netpol_test.sh` on a cluster with Calico.
The UI-reaches-API-only ingress rule (Guide Figure 3) is added with the workloads in P01.01.
See [DeploymentArchitecture](../docs/architecture/DeploymentArchitecture.md).
