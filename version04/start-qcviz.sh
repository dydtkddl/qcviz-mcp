#!/usr/bin/env bash
set -euo pipefail

source ~/miniconda3/etc/profile.d/conda.sh
conda activate qcviz

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

exec python -m uvicorn qcviz_mcp.web.app:app \
  --host 0.0.0.0 \
  --port 8817 \
  --ws wsproto \
  --app-dir src
