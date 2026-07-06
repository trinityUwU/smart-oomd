from monitor.history import HistoryTracker
from monitor.proc_reader import ProcessSample
from scoring.scorer import select_victim


def _proc(pid: int, name: str, rss_kb: int, ppid: int = 100, oom_score_adj: int = 0) -> ProcessSample:
    return ProcessSample(pid=pid, ppid=ppid, name=name, rss_kb=rss_kb, oom_score_adj=oom_score_adj)


def test_protected_process_never_selected() -> None:
    processes = [_proc(1, "systemd", rss_kb=999_999)]
    victim = select_victim(processes, HistoryTracker(), own_pid=999)
    assert victim is None


def test_own_pid_never_selected() -> None:
    processes = [_proc(42, "smart-oomd", rss_kb=999_999)]
    victim = select_victim(processes, HistoryTracker(), own_pid=42)
    assert victim is None


def test_largest_process_wins_without_growth_difference() -> None:
    processes = [_proc(10, "small", rss_kb=1000), _proc(11, "big", rss_kb=100_000)]
    victim = select_victim(processes, HistoryTracker(), own_pid=999)
    assert victim is not None
    assert victim.pid == 11


def test_oom_score_adj_never_kill_is_respected() -> None:
    processes = [_proc(20, "critical-svc", rss_kb=500_000, oom_score_adj=-1000)]
    victim = select_victim(processes, HistoryTracker(), own_pid=999)
    assert victim is None
