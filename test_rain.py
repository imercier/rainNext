# coding: utf-8
from meteofrance_api import MeteoFranceClient
import time


def test_rain() -> None:
    """Test rain forecast on a covered zone."""
    client = MeteoFranceClient()

    rain = client.get_rain(latitude=43.2959994, longitude=5.3754487)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rain.updated_on)))
    print(rain.forecast)


test_rain()
