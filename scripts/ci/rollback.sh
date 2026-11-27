#!/usr/bin/env sh
# usage: rollback.sh NAMESPACE
# Undoes only what the failed run changed. A Deployment with no earlier revision is scaled to zero.
set -eu
ns=$1
changed=${CHANGED_FILE:-.deployed}
[ -s "$changed" ] || { echo "this run changed no Deployment: nothing to roll back"; exit 0; }
failed=0
while read -r name; do
  if kubectl -n "$ns" rollout undo "deploy/$name" && kubectl -n "$ns" rollout status "deploy/$name" --timeout=180s; then
    echo "rolled back $name"
  else
    echo "$name has no usable previous revision: scaling to zero" >&2
    kubectl -n "$ns" scale "deploy/$name" --replicas=0 || failed=1
  fi
done < "$changed"
exit "$failed"
