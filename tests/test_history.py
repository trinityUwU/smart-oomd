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


def test_split_slopes_needs_four_samples() -> None:
    history = PidHistory(window_seconds=30.0)
    for t, v in [(0.0, 1000), (1.0, 900), (2.0, 800)]:
        history.samples.append((t, v))
    assert history.split_slopes() is None


def test_split_slopes_detects_deceleration() -> None:
    """Minecraft-like : perte forte au début, qui ralentit ensuite (approche d'un plateau)."""
    history = PidHistory(window_seconds=30.0)
    for t, v in [(0.0, 10000), (1.0, 8000), (2.0, 6500), (3.0, 5700), (4.0, 5400)]:
        history.samples.append((t, v))
    older_slope, recent_slope = history.split_slopes()
    assert older_slope < 0
    assert recent_slope > older_slope


def test_split_slopes_detects_constant_leak() -> None:
    """Fuite réelle : perte constante, pas de ralentissement."""
    history = PidHistory(window_seconds=30.0)
    for t, v in [(0.0, 10000), (1.0, 9000), (2.0, 8000), (3.0, 7000), (4.0, 6000)]:
        history.samples.append((t, v))
    older_slope, recent_slope = history.split_slopes()
    assert abs(recent_slope - older_slope) < 1.0
