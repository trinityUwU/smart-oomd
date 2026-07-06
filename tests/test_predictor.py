from monitor.history import PidHistory
from scoring.predictor import forecast_exhaustion


def test_decelerating_growth_is_flagged() -> None:
    """Minecraft-like : gros volume, mais la perte ralentit — pas une fuite."""
    history = PidHistory(window_seconds=30.0)
    for t, v in [(0.0, 10000), (1.0, 8000), (2.0, 6500), (3.0, 5700), (4.0, 5400)]:
        history.samples.append((t, v))
    forecast = forecast_exhaustion(history, available_kb=5400)
    assert forecast.is_decelerating is True


def test_constant_leak_is_not_flagged_as_decelerating() -> None:
    history = PidHistory(window_seconds=30.0)
    for t, v in [(0.0, 10000), (1.0, 9000), (2.0, 8000), (3.0, 7000), (4.0, 6000)]:
        history.samples.append((t, v))
    forecast = forecast_exhaustion(history, available_kb=6000)
    assert forecast.is_decelerating is False


def test_accelerating_leak_is_not_flagged_as_decelerating() -> None:
    history = PidHistory(window_seconds=30.0)
    for t, v in [(0.0, 10000), (1.0, 9500), (2.0, 8500), (3.0, 6500), (4.0, 3000)]:
        history.samples.append((t, v))
    forecast = forecast_exhaustion(history, available_kb=3000)
    assert forecast.is_decelerating is False
