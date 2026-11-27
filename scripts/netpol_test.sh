#!/usr/bin/env sh
set -eu
# Guide 9.3 evidence: a non-M5 pod must fail to reach the internet and an M5 pod must succeed.
# usage: netpol_test.sh [NAMESPACE]   (needs a cluster whose CNI enforces NetworkPolicy)
ns=${1:-idea-validator}
image=curlimages/curl:8.17.0
probe() { kubectl -n "$ns" run "$1" --rm -i --restart=Never --labels="$2" --image="$image" -- \
  curl -sS -m 10 -o /dev/null -w '%{http_code}\n' https://example.com; }
if probe netpol-denied app=netpol-test; then echo "FAIL: non-M5 pod reached the internet" >&2; exit 1; fi
echo "OK: non-M5 pod blocked"
probe netpol-allowed app=tools || { echo "FAIL: M5 pod cannot reach the internet" >&2; exit 1; }
echo "OK: M5 pod allowed"
