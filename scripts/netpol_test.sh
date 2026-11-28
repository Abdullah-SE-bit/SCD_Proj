#!/usr/bin/env sh
# Guide 9.3 and Figure 3: a non-M5 pod cannot reach the internet, an M5-labelled pod can, and the UI
# reaches the API only. Uses short-lived test pods, so no application workload is needed.
# usage: netpol_test.sh [NAMESPACE]   (first: cluster_up.sh, then kubectl apply -k k8s)
# KUBE_CONTEXT selects a cluster other than the current one. On Windows run it from Git Bash.
set -eu
export MSYS_NO_PATHCONV=1   # Git Bash must not rewrite /dev/null on its way into a container
ns=${1:-idea-validator}
curl_image=curlimages/curl:8.17.0@sha256:935d9100e9ba842cdb060de42472c7ca90cfe9a7c96e4dacb55e79e560b3ff40
server_image=busybox:1.37.0@sha256:a7dbc319b1438115a207e11930dc4bb3e643dcb3ec0bdd694bb36cd8fad289ec
site=https://example.com
pods="netpol-other netpol-tools netpol-ui netpol-gateway netpol-internal"

k() { kubectl ${KUBE_CONTEXT:+--context="$KUBE_CONTEXT"} -n "$ns" "$@"; }
# shellcheck disable=SC2086  # $pods is a word list
cleanup() { k delete pod $pods --ignore-not-found >/dev/null; }
fail() { echo "FAIL: $1" >&2; exit 1; }

# pod NAME APP IMAGE COMMAND. The readiness probe always fails, so no Service ever routes real traffic
# to a test pod that borrows an application label.
pod() {
  k apply -f - >/dev/null <<EOF
apiVersion: v1
kind: Pod
metadata: { name: $1, labels: { app: $2 } }
spec:
  restartPolicy: Never
  terminationGracePeriodSeconds: 0
  automountServiceAccountToken: false
  containers:
    - name: probe
      image: $3
      command: $4
      readinessProbe: { exec: { command: ["false"] } }
EOF
}

fetch() { k exec "$1" -- curl -4 -sS --connect-timeout 8 -m 15 -o /dev/null -w '%{http_code}' "$2" 2>&1; }
allowed() { # POD URL MEANING
  out=$(fetch "$1" "$2") || fail "$3: expected a connection, got: $out"
  echo "OK: $3 (HTTP $out)"
}
blocked() { # POD URL MEANING. Only a timeout (curl 28) counts: a dropped packet, not a broken probe.
  rc=0
  out=$(fetch "$1" "$2") || rc=$?
  [ "$rc" -ne 0 ] || fail "$3: expected a block, got HTTP $out"
  [ "$rc" -eq 28 ] || fail "$3: expected a timeout, got exit $rc: $out"
  echo "OK: $3 (timed out)"
}

cleanup
trap cleanup EXIT
pod netpol-other netpol-other "$curl_image" '["sleep", "600"]'
pod netpol-tools tools "$curl_image" '["sleep", "600"]'
pod netpol-ui ui "$curl_image" '["sleep", "600"]'
pod netpol-gateway gateway "$server_image" '["httpd", "-f", "-p", "8080", "-h", "/tmp"]'
pod netpol-internal netpol-internal "$server_image" '["httpd", "-f", "-p", "8080", "-h", "/tmp"]'
for p in $pods; do k wait --for=jsonpath='{.status.phase}'=Running "pod/$p" --timeout=180s >/dev/null; done
gateway=http://$(k get pod netpol-gateway -o jsonpath='{.status.podIP}'):8080/
internal=http://$(k get pod netpol-internal -o jsonpath='{.status.podIP}'):8080/

# Allowed paths come first: they show that the targets answer, so a later timeout means "blocked".
allowed netpol-tools "$site" "M5 pod (app=tools) reaches the internet"
allowed netpol-other "$internal" "a pod reaches another pod in the namespace"
allowed netpol-ui "$gateway" "UI (app=ui) reaches the API (app=gateway)"
for p in netpol-other netpol-ui; do
  k exec "$p" -- nslookup example.com >/dev/null 2>&1 || fail "$p cannot resolve DNS"
done
echo "OK: non-M5 pods resolve DNS"
blocked netpol-other "$site" "non-M5 pod cannot reach the internet"
blocked netpol-ui "$site" "UI cannot reach the internet"
blocked netpol-ui "$internal" "UI cannot reach any other service"
echo "PASS: network policies enforced in namespace $ns"
