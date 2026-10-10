import pytest

from src.price_watch_service import should_alert


def test_alerts_when_price_moves_five_percent():
    assert should_alert(10.0, 10.5)
    assert not should_alert(10.0, 10.49)


def test_previous_price_must_be_positive():
    with pytest.raises(ValueError):
        should_alert(0, 4)
