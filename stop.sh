#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PID_FILE="logs/smart-oomd.pid"

if [[ ! -f "${PID_FILE}" ]]; then
    echo "smart-oomd n'est pas lancé (pas de pidfile)"
    exit 0
fi

PID="$(cat "${PID_FILE}")"
if kill -0 "${PID}" 2>/dev/null; then
    kill "${PID}"
    echo "smart-oomd arrêté (pid ${PID})"
else
    echo "process ${PID} déjà mort"
fi
rm -f "${PID_FILE}"
