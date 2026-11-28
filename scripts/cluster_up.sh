#!/usr/bin/env sh
# usage: cluster_up.sh [NAME]
# One-node kind cluster with Calico, a network plugin that enforces NetworkPolicy. Safe to run again.
# Needs Docker, kind and kubectl. On Windows run it from Git Bash.
set -eu
name=${1:-idea-validator}
kind_version=0.33.0
node_image=kindest/node:v1.36.4@sha256:099e049362a1526b2db71494e1947aae99bd16290d7c895f2b7ea312e3cbfaed
calico_version=v3.33.1
calico_sha256=3368e62807b949438842e31f46c9b6df741731b4c755d0a622dd062b2cb20495

have=$(kind version -q) || { echo "kind $kind_version is required" >&2; exit 1; }
[ "$have" = "$kind_version" ] || { echo "kind $kind_version is required, found $have" >&2; exit 1; }

manifest=$(mktemp)
trap 'rm -f "$manifest"' EXIT
curl -fsSL -o "$manifest" "https://raw.githubusercontent.com/projectcalico/calico/$calico_version/manifests/calico.yaml"
echo "$calico_sha256  $manifest" | sha256sum -c - >/dev/null || { echo "Calico manifest checksum mismatch" >&2; exit 1; }

if kind get clusters | grep -qx "$name"; then
  echo "cluster $name already exists; applying Calico again"
else
  kind create cluster --name "$name" --image "$node_image" --config - <<'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  disableDefaultCNI: true     # no kindnet; Calico is installed below
  podSubnet: 192.168.0.0/16   # Calico's default address pool
nodes:
  - role: control-plane
EOF
fi

k() { kubectl --context "kind-$name" "$@"; }
k apply -f - < "$manifest"
k -n kube-system rollout status ds/calico-node --timeout=300s
k -n kube-system rollout status deploy/calico-kube-controllers --timeout=300s
k wait --for=condition=Ready nodes --all --timeout=180s
k -n kube-system rollout status deploy/coredns --timeout=180s
echo "cluster ready: context kind-$name, Calico $calico_version"
