#!/usr/bin/env bash
# Crée un scope systemd --user (cgroup v2 délégué, sans root) avec une limite
# mémoire basse, y lance stress-ng en dépassement volontaire, et lance le
# daemon scopé dessus pour vérifier qu'il tue avant le OOM killer du kernel.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

UNIT_NAME="smart-oomd-teststress-$$"
MEM_LIMIT_MB="${MEM_LIMIT_MB:-300}"
RUN_SECONDS="${RUN_SECONDS:-30}"

cleanup() {
    systemctl --user stop "${UNIT_NAME}.scope" 2>/dev/null || true
    pkill -9 -f "leak_sim.py" 2>/dev/null || true
}
trap cleanup EXIT

echo "[test_cgroup] lancement d'une fuite mémoire progressive (10MB/0.3s) dans un scope"
echo "[test_cgroup] systemd --user limité à ${MEM_LIMIT_MB}MB RAM, swap coupé (contrainte réelle)"

systemd-run --user --scope --unit="${UNIT_NAME}" \
    -p "MemoryMax=${MEM_LIMIT_MB}M" -p "MemorySwapMax=0" -- \
    python3 scripts/leak_sim.py \
    > /tmp/smart-oomd-stress.log 2>&1 &

sleep 1
CGROUP_PATH=$(find /sys/fs/cgroup -maxdepth 6 -name "${UNIT_NAME}.scope" 2>/dev/null | head -1)
if [[ -z "${CGROUP_PATH}" ]]; then
    echo "[test_cgroup] scope introuvable, abandon" >&2
    exit 1
fi
echo "[test_cgroup] cgroup: ${CGROUP_PATH}"

echo "[test_cgroup] lancement du daemon (dry-run désactivé, scope limité au test)"
timeout "${RUN_SECONDS}" env \
    SMART_OOMD_CGROUP_SCOPE="${CGROUP_PATH}" \
    SMART_OOMD_DRY_RUN=false \
    SMART_OOMD_THRESHOLD=15 \
    SMART_OOMD_POLL_INTERVAL=0.5 \
    .venv/bin/python -m daemon.main

echo "[test_cgroup] memory.events final:"
cat "${CGROUP_PATH}/memory.events" 2>/dev/null || echo "cgroup déjà nettoyé"
