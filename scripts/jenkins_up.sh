#!/usr/bin/env sh
# Start a local image registry and Jenkins next to the kind cluster (first: cluster_up.sh). Safe to run again;
# the Jenkins container is recreated, its home volume (job history) is kept.
# usage: jenkins_up.sh [BRANCH] [CLUSTER]   BRANCH is what Jenkins polls, default dev. On Windows use Git Bash.
set -eu
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
branch=${1:-dev}
cluster=${2:-idea-validator}
repo=${REPO_URL:-https://github.com/Abdullah-SE-bit/SCD_Proj.git}
port=${JENKINS_PORT:-8085}
node=$cluster-control-plane
registry_image=registry:3@sha256:82f6ff4a7f982960c8aa51617fea3aabc485df6e55cce80d22deb1de36f1bc3c

# 1. registry: pushed to as localhost:5001 by Docker, pulled by the cluster node under the same name
if ! docker inspect scd-registry >/dev/null 2>&1; then
  docker run -d --name scd-registry --restart unless-stopped --network kind -p 127.0.0.1:5001:5000 \
    "$registry_image" >/dev/null
fi
docker start scd-registry >/dev/null
docker exec "$node" sh -c '
  mkdir -p /etc/containerd/certs.d/localhost:5001
  printf "[host.\"http://scd-registry:5000\"]\n" > /etc/containerd/certs.d/localhost:5001/hosts.toml
  if grep -q "/etc/containerd/certs.d" /etc/containerd/config.toml; then exit 0; fi
  # kind ships the version 2 config format
  printf "\n[plugins.\"io.containerd.grpc.v1.cri\".registry]\n  config_path = \"/etc/containerd/certs.d\"\n" \
    >> /etc/containerd/config.toml
  systemctl restart containerd'

# 2. Jenkins, with Docker (the host socket) and the cluster (an in-network kubeconfig, held as a credential)
docker build -q -t scd-jenkins:local scripts/jenkins >/dev/null
docker rm -f scd-jenkins >/dev/null 2>&1 || true
docker create --name scd-jenkins --restart unless-stopped --network kind -p "127.0.0.1:$port:8080" \
  -v scd-jenkins-home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock \
  -e "REPO_URL=$repo" -e "REPO_BRANCH=*/$branch" scd-jenkins:local >/dev/null
kubeconfig=$(mktemp)
trap 'rm -f "$kubeconfig"' EXIT
kind get kubeconfig --internal --name "$cluster" > "$kubeconfig"
tar -C "$(dirname "$kubeconfig")" --transform "s|.*|kubeconfig-test|" -cf - "$(basename "$kubeconfig")" \
  | docker cp - scd-jenkins:/var/jenkins_home
docker start scd-jenkins >/dev/null
echo "Jenkins: http://127.0.0.1:$port/job/idea-validator-delivery/ (polls $branch); registry: localhost:5001"
