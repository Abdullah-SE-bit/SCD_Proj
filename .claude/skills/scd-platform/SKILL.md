---
name: scd-platform
description: SCD project rules for docker-engineering, kubernetes-engineering, cicd-engineering. Use when Dockerfiles, manifests, workflows or Jenkins.
---

# scd-platform

**Purpose:** project-specific rules for docker-engineering, kubernetes-engineering, cicd-engineering. Generic skills may help, but never override these.
**Use when:** Dockerfiles, manifests, workflows or Jenkins.
**Read first:** DeploymentArchitecture, CICDArchitecture.
**Requirements:** DKR-*, K8S-*, NET-*, CIC-*, JNK-*.

## Workflow
1. Multi-stage non-root pinned images, SHA tags
2. Probes on every workload; limits only from measurements
3. Test egress with scripts/netpol_test.sh
4. Pin actions by SHA, downloads by checksum
5. Demonstrate failure stops delivery and rollback works

**Tools:** docker, kind, kubectl, kubeconform, Trivy.
**Restrictions:** no `latest`, no secrets in files, no weakening checks, no `continue-on-error`. No secrets in files or messages.
**Verify:** `python harness/verification/scd.py check k8s-validate`, docker-build.
**Outputs:** manifests, run logs.
**On failure:** cluster cannot enforce policy: change CNI, do not drop the test.
**Complete when:** demonstrated and captured.
