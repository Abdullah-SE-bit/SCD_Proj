#!/usr/bin/env sh
set -eu
# usage: push_images.sh REGISTRY TAG
files=$(find services jobs -name Dockerfile)
[ -n "$files" ] || { echo "no Dockerfiles: nothing to push" >&2; exit 1; }
for f in $files; do
  docker push "$1/$(dirname "$f" | tr / -):$2"
done
