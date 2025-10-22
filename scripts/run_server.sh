#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 1 --log-level info

