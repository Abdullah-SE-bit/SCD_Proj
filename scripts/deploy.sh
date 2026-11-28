#!/usr/bin/env sh
# Build every module image, load it into the kind cluster and apply k8s/. Safe to run again.
# usage: deploy.sh [CLUSTER]   (first: cluster_up.sh). Needs Docker, kind and kubectl. On Windows use Git Bash.
set -eu
export MSYS_NO_PATHCONV=1   # Git Bash must not rewrite paths on their way into a container
cd "$(dirname "$0")/.."
cluster=${1:-idea-validator}
ns=idea-validator
tag=$(git rev-parse --short HEAD)
k() { kubectl --context "kind-$cluster" "$@"; }

for dockerfile in services/*/Dockerfile jobs/*/Dockerfile; do
  dir=${dockerfile%/Dockerfile}
  image="$(echo "$dir" | tr / -):$tag"
  echo "building $image"
  docker build -q -t "$image" "$dir" >/dev/null
  kind load docker-image "$image" --name "$cluster" >/dev/null
done

k apply -f k8s/namespace.yaml >/dev/null
# The database password is generated once, kept only in the cluster and never printed.
if ! k -n "$ns" get secret db-secret >/dev/null 2>&1; then
  password=$(od -An -N24 -tx1 /dev/urandom | tr -d ' \n')
  k -n "$ns" create secret generic db-secret --from-literal=POSTGRES_PASSWORD="$password" >/dev/null
  echo "created secret db-secret"
fi

# The key that signs login tokens, generated once the same way.
if ! k -n "$ns" get secret jwt-secret >/dev/null 2>&1; then
  signing=$(od -An -N48 -tx1 /dev/urandom | tr -d ' \n')
  k -n "$ns" create secret generic jwt-secret --from-literal=JWT_SIGNING_KEY="$signing" >/dev/null
  echo "created secret jwt-secret"
fi

k kustomize k8s | sed -E "s#(image: (services|jobs)-[a-z]+):dev#\1:$tag#" | k apply -f -
for workload in $(k -n "$ns" get deploy,statefulset -o name) ; do
  k -n "$ns" rollout status "$workload" --timeout=300s
done
k -n ingress rollout status deploy/traefik --timeout=300s
echo "deployed $tag. Open the app with: kubectl -n ingress port-forward svc/traefik 8080:80"
