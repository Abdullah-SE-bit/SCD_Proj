#!/usr/bin/env sh
# usage: rollback.sh NAMESPACE
# Undoes the Deployments the failed run changed. Only a Deployment with no earlier revision is scaled to
# zero; any other failure is reported and leaves the Deployment as it is.
set -eu
ns=$1
changed=${CHANGED_FILE:-${TMPDIR:-/tmp}/scd-deployed-$ns}
[ -s "$changed" ] || { echo "this run changed no Deployment: nothing to roll back"; exit 0; }
failed=0
while read -r name; do
  if ! history=$(kubectl -n "$ns" rollout history "deploy/$name"); then
    echo "FAIL: cannot read the history of $name; roll it back by hand" >&2
    failed=1
  elif [ "$(printf '%s\n' "$history" | grep -c '^[0-9]')" -lt 2 ]; then
    echo "$name is new in this run (no earlier revision): scaling to zero"
    kubectl -n "$ns" scale "deploy/$name" --replicas=0 || failed=1
  elif ! kubectl -n "$ns" rollout undo "deploy/$name"; then
    echo "FAIL: rollback of $name was refused" >&2
    failed=1
  elif ! kubectl -n "$ns" rollout status "deploy/$name" --timeout=180s; then
    echo "FAIL: $name was rolled back but is not ready yet; check it by hand" >&2
    failed=1
  else
    echo "rolled back $name"
  fi
done < "$changed"
exit "$failed"
