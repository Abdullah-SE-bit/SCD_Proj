#!/usr/bin/env sh
# usage: deploy.sh REGISTRY TAG NAMESPACE
# Manifests name images as REGISTRY/<module>:RELEASE. The tag is substituted and applied once, so each
# release is one revision. Deployments this run changed are listed in $CHANGED_FILE for rollback.sh.
set -eu
registry=$1 tag=$2 ns=$3
changed=${CHANGED_FILE:-.deployed}
before=$(mktemp) rendered=$(mktemp)
state() {
  kubectl -n "$ns" get deploy -o jsonpath='{range .items[*]}{.metadata.name} {.metadata.generation}{"\n"}{end}' | sort
}
: > "$changed"
kubectl kustomize k8s | sed "s#\(image: *$registry/[^:]*\):RELEASE#\1:$tag#" > "$rendered"
grep -q 'kind: Deployment' "$rendered" || { echo "no Deployments defined yet" >&2; exit 1; }
if grep -q ':RELEASE' "$rendered"; then echo "an image tag was not substituted" >&2; exit 1; fi
state > "$before"
record() { state | comm -13 "$before" - | cut -d' ' -f1 > "$changed"; }
trap record EXIT
kubectl apply -f "$rendered"
record
while read -r name; do
  kubectl -n "$ns" rollout status "deploy/$name" --timeout=180s
done < "$changed"
