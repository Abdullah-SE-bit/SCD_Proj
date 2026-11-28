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
expect=${SMOKE_EXPECT:-FIXTURE DATA}   # Jenkins sets another text to demonstrate a failing run
case $result in *"$expect"*) ;; *) fail "run answer does not contain '$expect'" ;; esac
echo "OK: UI to gateway through the ingress returns the labelled fixture verdict"
# 5. accounts and profile reach the database; search answers. Uses a throw-away account with a random password.
mail="smoke-$$-$(date +%s)@example.org"
secret=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
login="{\"email\":\"$mail\",\"password\":\"$secret\"}"
post() { curl -fsS -m 20 -H 'Content-Type: application/json' "$@"; }
post -d "$login" "$base/api/auth/register" >/dev/null || fail "register"
token=$(post -d "$login" "$base/api/auth/login" | sed -n 's/.*"token": *"\([^"]*\)".*/\1/p')
[ -n "$token" ] || fail "login returned no token"
profile='{"skills":["python"],"hours_per_week":10,"weeks_available":8,"team_size":2,"compute":"laptop","goal":"portfolio","interests":[]}'
post -X PUT -H "Authorization: Bearer $token" -d "$profile" "$base/api/profile" >/dev/null || fail "save profile"
saved=$(curl -fsS -m 20 -H "Authorization: Bearer $token" "$base/api/profile") || fail "read profile"
case $saved in *'"hours_per_week"'*) ;; *) fail "unexpected profile answer" ;; esac
curl -fsS -m 20 -H "Authorization: Bearer $token" "$base/api/ideas" >/dev/null || fail "history"
curl -fsS -m 20 "$base/api/metrics" | grep -q '"cache": "redis"' || fail "the cache is not connected"
echo "OK: register, log in, profile, history and cache metrics through the ingress"
found=$(k -n "$ns" exec deploy/gateway -- python -c '
import json, urllib.request
request = urllib.request.Request("http://kb:8000/search", json.dumps({"query": "study planner"}).encode(),
                                 {"Content-Type": "application/json"})
print(urllib.request.urlopen(request, timeout=120).read().decode()[:200])') || fail "knowledge base search"
echo "OK: knowledge base search answers: $(printf '%s' "$found" | cut -c1-80)"
echo "PASS: smoke test"
