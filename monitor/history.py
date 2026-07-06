"""Fenêtre glissante de mesures RSS par process, pour estimer une tendance de croissance."""

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class PidHistory:
    samples: deque[tuple[float, int]] = field(default_factory=deque)
    window_seconds: float = 30.0

    def push(self, rss_kb: int) -> None:
        now = time.monotonic()
        self.samples.append((now, rss_kb))
        cutoff = now - self.window_seconds
        while self.samples and self.samples[0][0] < cutoff:
            self.samples.popleft()

    def growth_rate_kb_per_s(self) -> float:
        """Pente de régression linéaire (moindres carrés) sur la fenêtre courante."""
        if len(self.samples) < 2:
            return 0.0

        t0 = self.samples[0][0]
        xs = [t - t0 for t, _ in self.samples]
        ys = [float(rss) for _, rss in self.samples]
        n = len(xs)

        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        denominator = sum((x - mean_x) ** 2 for x in xs)

        if denominator == 0:
            return 0.0
        return numerator / denominator

    def latest_rss_kb(self) -> int:
        return self.samples[-1][1] if self.samples else 0


class HistoryTracker:
    """Maintient l'historique de tous les PID surveillés et purge ceux disparus."""

    def __init__(self, window_seconds: float = 30.0) -> None:
        self._window_seconds = window_seconds
        self._by_pid: dict[int, PidHistory] = {}

    def update(self, pid: int, rss_kb: int) -> PidHistory:
        history = self._by_pid.setdefault(pid, PidHistory(window_seconds=self._window_seconds))
        history.push(rss_kb)
        return history

    def prune(self, live_pids: set[int]) -> None:
        for pid in list(self._by_pid):
            if pid not in live_pids:
                del self._by_pid[pid]

    def get(self, pid: int) -> PidHistory | None:
        return self._by_pid.get(pid)
