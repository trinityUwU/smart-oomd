"""Prédiction du temps avant épuisement mémoire, à partir de la tendance système."""

from dataclasses import dataclass

from monitor.history import PidHistory


@dataclass(frozen=True)
class ExhaustionForecast:
    available_kb: int
    trend_kb_per_s: float
    seconds_remaining: float | None
    is_decelerating: bool


def _is_decelerating(available_history: PidHistory) -> bool:
    """True si la perte de mémoire ralentit (approche d'un plateau, pas une fuite)."""
    slopes = available_history.split_slopes()
    if slopes is None:
        return False

    older_slope, recent_slope = slopes
    return older_slope < 0 and recent_slope > older_slope


def forecast_exhaustion(available_history: PidHistory, available_kb: int) -> ExhaustionForecast:
    """None de seconds_remaining = mémoire disponible stable ou en hausse, pas de risque détecté."""
    trend = available_history.growth_rate_kb_per_s()
    is_decelerating = _is_decelerating(available_history)

    if trend >= 0:
        return ExhaustionForecast(
            available_kb=available_kb,
            trend_kb_per_s=trend,
            seconds_remaining=None,
            is_decelerating=is_decelerating,
        )

    seconds_remaining = available_kb / -trend
    return ExhaustionForecast(
        available_kb=available_kb,
        trend_kb_per_s=trend,
        seconds_remaining=seconds_remaining,
        is_decelerating=is_decelerating,
    )
