import requests


BTC_TURK_URL = "https://api.btcturk.com/api/v2/ticker?pairSymbol=USDTTRY"
BINANCE_SPOT_URL = "https://api.binance.com/api/v3/ticker/price?symbol=USDTTRY"


def get_usdt_try():
    """Возвращает TRY за 1 USDT, с Binance Spot как резервным источником."""
    try:
        response = requests.get(BTC_TURK_URL, timeout=10)
        response.raise_for_status()
        return float(response.json()["data"][0]["last"])
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        response = requests.get(BINANCE_SPOT_URL, timeout=10)
        response.raise_for_status()
        return float(response.json()["price"])

