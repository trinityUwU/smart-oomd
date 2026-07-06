"""Configuration du daemon, entièrement pilotable par variables d'environnement."""

import os
from dataclasses import dataclass


def _env_float(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes")


def _env_int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


@dataclass(frozen=True)
class DaemonConfig:
    poll_interval_seconds: float
    history_window_seconds: float
    exhaustion_threshold_seconds: float
    dry_run: bool
    cgroup_scope_path: str | None
    min_available_percent: float
    consecutive_confirmations: int

    @staticmethod
    def from_env() -> "DaemonConfig":
        return DaemonConfig(
            poll_interval_seconds=_env_float("SMART_OOMD_POLL_INTERVAL", 1.0),
            history_window_seconds=_env_float("SMART_OOMD_HISTORY_WINDOW", 30.0),
            exhaustion_threshold_seconds=_env_float("SMART_OOMD_THRESHOLD", 15.0),
            dry_run=_env_bool("SMART_OOMD_DRY_RUN", True),
            cgroup_scope_path=os.environ.get("SMART_OOMD_CGROUP_SCOPE"),
            min_available_percent=_env_float("SMART_OOMD_MIN_AVAILABLE_PERCENT", 10.0),
            consecutive_confirmations=_env_int("SMART_OOMD_CONFIRMATIONS", 3),
        )
