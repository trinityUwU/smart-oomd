"""Point d'entrée du daemon : boucle de surveillance, prédiction, kill préventif."""

import os
import time
from pathlib import Path

from loguru import logger

from daemon.config import DaemonConfig
from killer.executor import kill_candidate
from monitor.history import HistoryTracker, PidHistory
from monitor.proc_reader import (
    list_processes,
    read_cgroup_available_kb,
    read_cgroup_pids,
    read_meminfo_kb,
)
from scoring.predictor import forecast_exhaustion
from scoring.scorer import select_victim


def _resolve_pids_filter(cgroup_scope_path: str | None) -> set[int] | None:
    if cgroup_scope_path is None:
        return None
    return read_cgroup_pids(Path(cgroup_scope_path))


def _read_available_kb(cgroup_scope_path: str | None) -> int:
    if cgroup_scope_path is None:
        return read_meminfo_kb().get("MemAvailable", 0)

    available = read_cgroup_available_kb(Path(cgroup_scope_path))
    if available is not None:
        return available

    logger.warning(f"cgroup {cgroup_scope_path} sans memory.max — repli sur la mémoire système")
    return read_meminfo_kb().get("MemAvailable", 0)


def run(config: DaemonConfig) -> None:
    own_pid = os.getpid()
    process_history = HistoryTracker(window_seconds=config.history_window_seconds)
    available_history = PidHistory(window_seconds=config.history_window_seconds)

    logger.info(
        f"smart-oomd démarré: dry_run={config.dry_run} threshold={config.exhaustion_threshold_seconds}s "
        f"scope={config.cgroup_scope_path or 'système entier'}"
    )

    while True:
        if config.cgroup_scope_path is not None and not Path(config.cgroup_scope_path).exists():
            logger.info(f"scope {config.cgroup_scope_path} disparu — plus rien à surveiller, arrêt")
            return

        available_kb = _read_available_kb(config.cgroup_scope_path)
        available_history.push(available_kb)

        forecast = forecast_exhaustion(available_history, available_kb)
        if forecast.seconds_remaining is not None:
            logger.debug(
                f"tendance mémoire: {forecast.trend_kb_per_s:.0f}kB/s, "
                f"épuisement estimé dans {forecast.seconds_remaining:.1f}s"
            )

        pids_filter = _resolve_pids_filter(config.cgroup_scope_path)
        processes = list_processes(pids_filter)
        process_history.prune({p.pid for p in processes})

        should_act = (
            forecast.seconds_remaining is not None
            and forecast.seconds_remaining < config.exhaustion_threshold_seconds
        )
        if should_act:
            victim = select_victim(processes, process_history, own_pid)
            if victim is not None:
                kill_candidate(victim, config.dry_run)
            else:
                logger.warning("épuisement imminent mais aucun candidat éligible trouvé")

        time.sleep(config.poll_interval_seconds)


def main() -> None:
    config = DaemonConfig.from_env()
    try:
        run(config)
    except KeyboardInterrupt:
        logger.info("arrêt demandé (SIGINT)")


if __name__ == "__main__":
    main()
