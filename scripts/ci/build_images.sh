#!/usr/bin/env sh
set -eu
# usage: build_images.sh REGISTRY TAG
files=$(find services jobs -name Dockerfile)
[ -n "$files" ] || { echo "no Dockerfiles: nothing to build" >&2; exit 1; }
for f in $files; do
  dir=$(dirname "$f")
  docker build -t "$1/$(echo "$dir" | tr / -):$2" "$dir"
done
