#!/usr/bin/env bash
# Deux fuites concurrentes (une rapide, une lente) dans le même scope, pour
# vérifier que le score composite cible bien la plus dangereuse, pas juste
# la plus grosse à l'instant T.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

UNIT_NAME="smart-oomd-multitest-$$"
MEM_LIMIT_MB="${MEM_LIMIT_MB:-400}"
RUN_SECONDS="${RUN_SECONDS:-25}"

cleanup() {
    systemctl --user stop "${UNIT_NAME}.scope" 2>/dev/null || true
    pkill -9 -f "leak_sim.py" 2>/dev/null || true
}
trap cleanup EXIT

echo "[multi] scope limité à ${MEM_LIMIT_MB}MB, swap coupé"
echo "[multi] leaker A (rapide, 0.1s/10MB) + leaker B (lent, 1.0s/10MB)"

systemd-run --user --scope --unit="${UNIT_NAME}" \
    -p "MemoryMax=${MEM_LIMIT_MB}M" -p "MemorySwapMax=0" -- \
    bash -c "python3 scripts/leak_sim.py 0.1 & python3 scripts/leak_sim.py 1.0 & wait" \
    > /tmp/smart-oomd-multi.log 2>&1 &

sleep 1.5
CGROUP_PATH=$(find /sys/fs/cgroup -maxdepth 8 -name "${UNIT_NAME}.scope" 2>/dev/null | head -1)
if [[ -z "${CGROUP_PATH}" ]]; then
    echo "[multi] scope introuvable, abandon" >&2
    exit 1
fi
echo "[multi] cgroup: ${CGROUP_PATH}"
echo "[multi] pids dans le scope avant kill:"
cat "${CGROUP_PATH}/cgroup.procs" 2>/dev/null

timeout "${RUN_SECONDS}" env \
    SMART_OOMD_CGROUP_SCOPE="${CGROUP_PATH}" \
    SMART_OOMD_DRY_RUN=false \
    SMART_OOMD_THRESHOLD=15 \
    SMART_OOMD_POLL_INTERVAL=0.5 \
    .venv/bin/python -m daemon.main

echo "[multi] memory.events final:"
cat "${CGROUP_PATH}/memory.events" 2>/dev/null || echo "cgroup déjà nettoyé"
