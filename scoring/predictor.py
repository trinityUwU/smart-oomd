"""Prédiction du temps avant épuisement mémoire, à partir de la tendance système."""

from dataclasses import dataclass

from monitor.history import PidHistory


@dataclass(frozen=True)
class ExhaustionForecast:
    available_kb: int
    trend_kb_per_s: float
    seconds_remaining: float | None


def forecast_exhaustion(available_history: PidHistory, available_kb: int) -> ExhaustionForecast:
    """None de seconds_remaining = mémoire disponible stable ou en hausse, pas de risque détecté."""
    trend = available_history.growth_rate_kb_per_s()
    if trend >= 0:
        return ExhaustionForecast(available_kb=available_kb, trend_kb_per_s=trend, seconds_remaining=None)

    seconds_remaining = available_kb / -trend
    return ExhaustionForecast(available_kb=available_kb, trend_kb_per_s=trend, seconds_remaining=seconds_remaining)
