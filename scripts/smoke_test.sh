#!/usr/bin/env sh
# Real probes against the running cluster (first: deploy.sh). Fails on the first thing that does not answer.
# usage: smoke_test.sh [CLUSTER]   Needs kubectl and curl. On Windows run it from Git Bash.
set -eu
export MSYS_NO_PATHCONV=1
cluster=${1:-idea-validator}
ns=idea-validator
port=${SMOKE_PORT:-18080}
k() { kubectl --context "kind-$cluster" "$@"; }
fail() { echo "FAIL: $1" >&2; exit 1; }

# 1. every workload has all its replicas available
for workload in $(k -n "$ns" get deploy,statefulset -o name) ingress:deployment.apps/traefik; do
  space=$ns
  case $workload in ingress:*) space=ingress; workload=${workload#ingress:} ;; esac
  want=$(k -n "$space" get "$workload" -o jsonpath='{.spec.replicas}')
  have=$(k -n "$space" get "$workload" -o jsonpath='{.status.readyReplicas}')
  [ "$want" -gt 0 ] && [ "${have:-0}" = "$want" ] || fail "$workload: ${have:-0} of $want replicas ready"
done
echo "OK: every workload is ready"

# 2. every service answers /health and /ready through its Service name, asked from inside the namespace
k -n "$ns" exec deploy/gateway -- python -c '
import sys, urllib.request
names = "gateway profile orchestrator tools scouts kb analyst ideation validators scorer verdict critic agentops"
bad = []
for name, port in [(n, 8000) for n in names.split()] + [("ui", 8080)]:
    for path in ("/health", "/ready"):
        try:
            urllib.request.urlopen(f"http://{name}:{port}{path}", timeout=5).read()
        except Exception as error:
            bad.append(f"{name}{path}: {type(error).__name__}")
for line in bad:
    print("FAIL:", line)
print("OK: 14 services answer /health and /ready" if not bad else f"{len(bad)} probes failed")
sys.exit(1 if bad else 0)
' || fail "service probes"

# 3. data stores
k -n "$ns" exec statefulset/postgres -- pg_isready -q -h 127.0.0.1 -U app -d idea_validator || fail "postgres not ready"
[ "$(k -n "$ns" exec deploy/redis -- redis-cli ping | tr -d '\r')" = PONG ] || fail "redis did not answer PONG"
k -n "$ns" exec deploy/gateway -- python -c '
import urllib.request; urllib.request.urlopen("http://qdrant:6333/readyz", timeout=5)' || fail "qdrant not ready"
echo "OK: postgres, redis and qdrant answer"

# 4. the single entry point: Ingress to the UI, and through the UI to the gateway
log=$(mktemp)
k -n ingress port-forward svc/traefik "$port:80" >"$log" 2>&1 &
forward=$!
trap 'kill "$forward" 2>/dev/null || true; rm -f "$log"' EXIT
base=http://127.0.0.1:$port
tries=0
until curl -fsS -m 3 "$base/" >/dev/null 2>&1; do   # no -o /dev/null: Windows curl cannot open that path
  tries=$((tries + 1))
  [ "$tries" -lt 20 ] || fail "ingress does not serve the UI: $(cat "$log")"
  sleep 1
done
echo "OK: ingress serves the UI"
run=$(curl -fsS -m 10 -H 'Content-Type: application/json' -d '{"idea":"smoke test idea"}' "$base/api/validate") \
  || fail "POST /api/validate through the ingress"
case $run in *run_id*) ;; *) fail "unexpected validate answer: $run" ;; esac
result=$(curl -fsS -m 10 "$base/api/runs/fixture-run") || fail "GET /api/runs through the ingress"
case $result in *"FIXTURE DATA"*) ;; *) fail "unexpected run answer" ;; esac
echo "OK: UI to gateway through the ingress returns the labelled fixture verdict"
echo "PASS: smoke test"
