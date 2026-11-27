#!/usr/bin/env sh
set -eu
# usage: deploy.sh REGISTRY TAG NAMESPACE
kubectl apply -k k8s
deployments=$(kubectl -n "$3" get deploy -o name)
[ -n "$deployments" ] || { echo "no Deployments defined yet" >&2; exit 1; }
for d in $deployments; do
  name=${d#*/}
  kubectl -n "$3" set image "$d" "$name=$1/$name:$2"
  kubectl -n "$3" rollout status "$d" --timeout=180s
done
