#!/usr/bin/env sh
# usage: deploy.sh REGISTRY TAG NAMESPACE
# Manifests name images <area>-<module>:dev. Registry and tag are substituted and applied once, so each
# release is one revision. Deployments this run changed are listed in $CHANGED_FILE for rollback.sh.
set -eu
registry=$1 tag=$2 ns=$3
changed=${CHANGED_FILE:-${TMPDIR:-/tmp}/scd-deployed-$ns}
before=$(mktemp) rendered=$(mktemp)
# Compare pod templates: only a template change creates a revision that "rollout undo" can reverse. Other
# changes (replica counts, ConfigMaps) are not rolled back by this pipeline.
state() {
  kubectl -n "$ns" get deploy -o jsonpath='{range .items[*]}{.metadata.name} {.spec.template}{"\n"}{end}' | sort
}
: > "$changed"
kubectl kustomize k8s | sed -E "s#(image: *)((services|jobs)-[a-z]+):dev#\1$registry/\2:$tag#" > "$rendered"
grep -q 'kind: Deployment' "$rendered" || { echo "no Deployments defined yet" >&2; exit 1; }
if grep -qE 'image: *(services|jobs)-' "$rendered"; then echo "an image tag was not substituted" >&2; exit 1; fi
kubectl apply -f k8s/namespace.yaml
# The database password is generated once, kept only in the cluster and never printed.
if ! kubectl -n "$ns" get secret db-secret >/dev/null 2>&1; then
  password=$(od -An -N24 -tx1 /dev/urandom | tr -d ' \n')
  kubectl -n "$ns" create secret generic db-secret --from-literal=POSTGRES_PASSWORD="$password" >/dev/null
fi
state > "$before"
record() { state | comm -13 "$before" - | cut -d' ' -f1 > "$changed"; }
trap record EXIT
kubectl apply -f "$rendered"
record
while read -r name; do
  kubectl -n "$ns" rollout status "deploy/$name" --timeout=180s
done < "$changed"
