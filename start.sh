#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PID_FILE="logs/smart-oomd.pid"
LOG_FILE="logs/smart-oomd.log"

mkdir -p logs
: > "${LOG_FILE}"

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
    echo "smart-oomd tourne déjà (pid $(cat "${PID_FILE}"))"
    exit 0
fi

nohup .venv/bin/python -m daemon.main >> "${LOG_FILE}" 2>&1 &
echo $! > "${PID_FILE}"
echo "smart-oomd démarré (pid $!)"
