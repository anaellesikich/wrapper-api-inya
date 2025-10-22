#!/usr/bin/env bash
set -euo pipefail
IMAGE=${IMAGE:-my-gpt-wrapper:local}
docker build -t "$IMAGE" .
