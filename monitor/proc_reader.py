"""Lecture des process actifs et de leur empreinte mémoire via /proc."""

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

PROC_ROOT = Path("/proc")


@dataclass(frozen=True)
class ProcessSample:
    pid: int
    ppid: int
    name: str
    rss_kb: int
    oom_score_adj: int


def _read_status(pid_dir: Path) -> tuple[int, str, int] | None:
    try:
        ppid = 0
        name = ""
        oom_score_adj = 0
        for line in (pid_dir / "status").read_text().splitlines():
            if line.startswith("Name:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("PPid:"):
                ppid = int(line.split(":", 1)[1].strip())
        oom_score_adj = int((pid_dir / "oom_score_adj").read_text().strip())
        return ppid, name, oom_score_adj
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError) as exc:
        logger.trace(f"status illisible pour {pid_dir.name}: {exc}")
        return None


def _read_rss_kb(pid_dir: Path) -> int | None:
    try:
        fields = (pid_dir / "statm").read_text().split()
        page_kb = 4
        return int(fields[1]) * page_kb
    except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError, IndexError) as exc:
        logger.trace(f"statm illisible pour {pid_dir.name}: {exc}")
        return None


def list_processes(pids_filter: set[int] | None = None) -> list[ProcessSample]:
    """Snapshot des process vivants, filtrable sur un sous-ensemble de PID (ex: un cgroup)."""
    samples: list[ProcessSample] = []
    for entry in PROC_ROOT.iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pids_filter is not None and pid not in pids_filter:
            continue

        status = _read_status(entry)
        rss_kb = _read_rss_kb(entry)
        if status is None or rss_kb is None:
            continue

        ppid, name, oom_score_adj = status
        samples.append(ProcessSample(pid=pid, ppid=ppid, name=name, rss_kb=rss_kb, oom_score_adj=oom_score_adj))
    return samples


def read_meminfo_kb() -> dict[str, int]:
    """MemTotal / MemAvailable / SwapFree en kB, tels qu'exposés par /proc/meminfo."""
    result: dict[str, int] = {}
    try:
        for line in (PROC_ROOT / "meminfo").read_text().splitlines():
            key, _, rest = line.partition(":")
            if key in ("MemTotal", "MemAvailable", "SwapFree"):
                result[key] = int(rest.strip().split()[0])
    except (FileNotFoundError, PermissionError, ValueError) as exc:
        logger.error(f"lecture /proc/meminfo échouée: {exc}")
    return result


def read_cgroup_pids(cgroup_path: Path) -> set[int]:
    """PIDs appartenant à un cgroup v2 (ex: /sys/fs/cgroup/smart-oomd-test/cgroup.procs)."""
    try:
        return {int(line) for line in (cgroup_path / "cgroup.procs").read_text().split()}
    except (FileNotFoundError, PermissionError, ValueError) as exc:
        logger.error(f"lecture cgroup.procs échouée pour {cgroup_path}: {exc}")
        return set()
