#!/usr/bin/env sh
set -eu
# Succeeds only when at least one module has a Dockerfile.
find services jobs -name Dockerfile 2>/dev/null | grep -q .
