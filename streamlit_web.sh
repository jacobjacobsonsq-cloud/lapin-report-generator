#!/bin/bash

set -euo pipefail

PORT="${PORT:-8501}"
BASE_URL_PATH="${BASE_URL_PATH:-}"

STREAMLIT_BIN="streamlit"
if [[ -x "./venv/bin/streamlit" ]]; then
  STREAMLIT_BIN="./venv/bin/streamlit"
fi

ARGS=(
  "run" "app.py"
  "--server.headless=true"
  "--server.address=0.0.0.0"
  "--server.port=${PORT}"
  "--browser.gatherUsageStats=false"
  "--server.fileWatcherType=none"
)

if [[ -n "${BASE_URL_PATH}" ]]; then
  ARGS+=("--server.baseUrlPath=${BASE_URL_PATH}")
fi

exec "${STREAMLIT_BIN}" "${ARGS[@]}"
