#!/usr/bin/env sh
set -eu
# usage: rollback.sh NAMESPACE
for d in $(kubectl -n "$1" get deploy -o name); do
  kubectl -n "$1" rollout undo "$d"
  kubectl -n "$1" rollout status "$d" --timeout=180s
done
