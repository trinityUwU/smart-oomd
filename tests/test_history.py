import time

from monitor.history import HistoryTracker, PidHistory


def test_growth_rate_needs_two_samples() -> None:
    history = PidHistory(window_seconds=30.0)
    history.push(1000)
    assert history.growth_rate_kb_per_s() == 0.0


def test_growth_rate_detects_upward_trend() -> None:
    history = PidHistory(window_seconds=30.0)
    history.samples.append((0.0, 1000))
    history.samples.append((1.0, 2000))
    history.samples.append((2.0, 3000))
    assert history.growth_rate_kb_per_s() == 1000.0


def test_growth_rate_detects_downward_trend() -> None:
    history = PidHistory(window_seconds=30.0)
    history.samples.append((0.0, 3000))
    history.samples.append((1.0, 2000))
    history.samples.append((2.0, 1000))
    assert history.growth_rate_kb_per_s() == -1000.0


def test_window_evicts_old_samples() -> None:
    history = PidHistory(window_seconds=5.0)
    now = time.monotonic()
    history.samples.append((now - 10.0, 500))
    history.push(1000)
    assert len(history.samples) == 1


def test_tracker_prunes_dead_pids() -> None:
    tracker = HistoryTracker()
    tracker.update(pid=1, rss_kb=100)
    tracker.update(pid=2, rss_kb=200)
    tracker.prune(live_pids={1})
    assert tracker.get(1) is not None
    assert tracker.get(2) is None
