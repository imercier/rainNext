#! /usr/bin/python3

# coding: utf-8
from meteofrance_api import MeteoFranceClient
import time
import json


def test_rain() -> None:
    """Test rain forecast on a covered zone."""
    client = MeteoFranceClient()

    rain = client.get_rain(latitude=43.2959994, longitude=5.3754487)
    print(int(time.time()))
    print(json.dumps(rain.forecast))


test_rain()
