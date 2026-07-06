#!/usr/bin/env bash
# Crée un cgroup v2 isolé avec une limite mémoire basse, y lance stress-ng pour
# simuler une fuite mémoire, et confine le kill préventif à ce seul cgroup.
set -euo pipefail

CGROUP_NAME="smart-oomd-test"
CGROUP_PATH="/sys/fs/cgroup/${CGROUP_NAME}"
MEM_LIMIT_MB="${MEM_LIMIT_MB:-300}"

cleanup() {
    echo "[test_cgroup] nettoyage du cgroup ${CGROUP_NAME}"
    if [[ -d "${CGROUP_PATH}" ]]; then
        pkill -9 -f "stress-ng" 2>/dev/null || true
        sleep 0.5
        rmdir "${CGROUP_PATH}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

if ! command -v stress-ng >/dev/null; then
    echo "stress-ng manquant — installe-le avec: sudo pacman -S stress-ng" >&2
    exit 1
fi

sudo mkdir -p "${CGROUP_PATH}"
sudo bash -c "echo $((MEM_LIMIT_MB * 1024 * 1024)) > ${CGROUP_PATH}/memory.max"

echo "[test_cgroup] cgroup ${CGROUP_NAME} limité à ${MEM_LIMIT_MB}MB"
echo "[test_cgroup] lancement de stress-ng dans le cgroup (croissance mémoire simulée)"

sudo bash -c "
    echo \$\$ > ${CGROUP_PATH}/cgroup.procs
    exec stress-ng --vm 1 --vm-bytes ${MEM_LIMIT_MB}M --vm-hang 0 --timeout 60s
" &
STRESS_SHELL_PID=$!

echo "[test_cgroup] daemon à lancer manuellement dans un autre terminal:"
echo "  cd /mnt/projects/smart-oomd"
echo "  SMART_OOMD_CGROUP_SCOPE=${CGROUP_PATH} SMART_OOMD_DRY_RUN=false SMART_OOMD_THRESHOLD=20 \\"
echo "    .venv/bin/python -m daemon.main"
echo "[test_cgroup] observe: le daemon doit tuer le worker stress-ng avant que le cgroup OOM kill le tout."

wait "${STRESS_SHELL_PID}"
