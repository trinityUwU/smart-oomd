"""Sélection de la victime : score composite croissance + taille, hors process protégés."""

from dataclasses import dataclass

from monitor.history import HistoryTracker
from monitor.proc_reader import ProcessSample
from scoring.criticality import is_protected

WEIGHT_GROWTH = 0.6
WEIGHT_SIZE = 0.4


@dataclass(frozen=True)
class ScoredCandidate:
    pid: int
    name: str
    rss_kb: int
    growth_kb_per_s: float
    score: float


def _normalize(value: float, max_value: float) -> float:
    return value / max_value if max_value > 0 else 0.0


def select_victim(
    processes: list[ProcessSample],
    history: HistoryTracker,
    own_pid: int,
) -> ScoredCandidate | None:
    eligible = [p for p in processes if not is_protected(p.pid, p.name, p.oom_score_adj, own_pid)]
    if not eligible:
        return None

    growths = {p.pid: max(history.update(p.pid, p.rss_kb).growth_rate_kb_per_s(), 0.0) for p in eligible}
    max_growth = max(growths.values(), default=0.0)
    max_rss = max((p.rss_kb for p in eligible), default=0)

    best: ScoredCandidate | None = None
    for proc in eligible:
        growth_score = _normalize(growths[proc.pid], max_growth)
        size_score = _normalize(proc.rss_kb, max_rss)
        score = WEIGHT_GROWTH * growth_score + WEIGHT_SIZE * size_score

        if best is None or score > best.score:
            best = ScoredCandidate(
                pid=proc.pid,
                name=proc.name,
                rss_kb=proc.rss_kb,
                growth_kb_per_s=growths[proc.pid],
                score=score,
            )

    return best
