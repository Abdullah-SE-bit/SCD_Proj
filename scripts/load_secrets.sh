#!/usr/bin/env sh
# Copy the external API keys from .env into the cluster secret "api-keys" without printing them.
# Only the names below are copied; empty ones are skipped. usage: load_secrets.sh [CLUSTER]
set -eu
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
cluster=${1:-idea-validator}
[ -f .env ] || { echo ".env not found; copy .env.example to .env and fill it in" >&2; exit 1; }

keys=$(mktemp)
trap 'rm -f "$keys"' EXIT
grep -E '^(HOSTED_LLM_BASE_URL|HOSTED_LLM_API_KEY|HOSTED_LLM_MODEL|GITHUB_API_TOKEN|PRODUCT_HUNT_TOKEN|JWT_SIGNING_KEY)=.' .env \
  | tr -d '\r' > "$keys" || { echo "no API key has a value in .env" >&2; exit 1; }

k() { kubectl --context "kind-$cluster" -n idea-validator "$@"; }
k create secret generic api-keys --from-env-file="$keys" --dry-run=client -o yaml | k apply -f - >/dev/null
echo "secret api-keys holds: $(cut -d= -f1 "$keys" | tr '\n' ' ')"
